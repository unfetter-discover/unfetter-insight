###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists for training and validation of the unfetter.io model
# It acts very differently from other models here in that it uses only the 
# wikis for training. we take the convoluded text of each wiki and use it to 
# build a classifier for each individual wiki. It is tested on the report set.
# Author: William Kinsman
# Date: 2016_01_26
###############################################################################
# IMPORTS                                                                     #
###############################################################################
import os
import re
import sys
import pickle
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text as STOPWORDS
from sklearn.naive_bayes import MultinomialNB
from collections import Counter

# babelfish native imports
from text_tools.preprocessing import preprocess,stem_all,remove_reference_tags
from text_tools.convolution import convolve_text,tf_vectorizer
###############################################################################
# DATA LOADING                                                                #
###############################################################################
def main():

    ###########################################################################
    # MODEL CUSTOMIZATIONS                                                    #
    ###########################################################################
    min_ngram_freq = 3              # min freq required to be added to vocab (2 is slightly better, but longer runtime)
    max_ngram = 1                   # max number of words allowed in a vocab term
    regex = r'\b([A-Za-z]{3,}|[0-9]+[A-Za-z]{2,}|[A-Za-z]{2,}[0-9]+|[A-Za-z]+[0-9]+[A-Za-z]+)\b'  # acceptable words
    windowsize = 500                # character size of the sliding window.
    step = 1                        # number of characters to step per slide.
    parallel = False                 # run training in parallel?
    more_stopwords = ['like','use','uses','used','using','able','aid','aids'] # additional stopwords beyond standard
    stopwords = list(STOPWORDS.ENGLISH_STOP_WORDS.union(more_stopwords))
    
    ###########################################################################
    # CONSTRUCT CONVOLUTIONS AND VOCABULARY                                   #
    ###########################################################################
    # build tokenizer
    tokenizer = CountVectorizer(encoding='utf-8',decode_error='ignore',
                                lowercase=False,ngram_range=(1,max_ngram),
                                token_pattern=regex,stop_words=stopwords)  
    tokenizer = tokenizer.build_analyzer()
    
    #get dictionary
    dir_sp = sys.path
    coefdir = None
    for i in range(len(dir_sp)):
        if os.path.isdir(os.path.join(dir_sp[i],'babelfish')):
            coefdir = os.path.join(dir_sp[i],'babelfish')
            break
    assert coefdir!=None, "Could not locate site-packages directory with babelfish. Aborting."
    
    with open(os.path.join(coefdir,'dict_wiki')) as f:
        wiki_dict = pickle.load(f)  # wiki texts
    keys = wiki_dict.keys()
    keys.sort()
    convolutions = []
    
    # preprocessing
    for k,v in wiki_dict.items():
        wiki_dict[k] = preprocess(wiki_dict[k])
        wiki_dict[k] = remove_reference_tags(wiki_dict[k])
        wiki_dict[k] = stem_all(wiki_dict[k],'porter')
    
    # build vocabulary
    all_text = '\n'.join(wiki_dict.values())
    vocabulary = build_vocab(tokenizer,all_text,min_ngram_freq)
    
    # build text windows
    convolutions = []
    for key in keys:
        convolutions.append(convolve_text(wiki_dict[key],windowsize=windowsize,step=step,
                                  ws_trim=False,word_trim=True,fence=False))
    
    ###########################################################################
    # TRAINING                                                                #
    ###########################################################################
    all_convolutions = [item for sublist in convolutions for item in sublist]
    input_vectors = tf_vectorizer(all_convolutions,vocabulary,parallel=parallel)
    output_vectors = generate_output_vectors(convolutions)
    
    # build coefficients for each classifier
    coef = []
    for i in xrange(len(keys)):
        coef.append(MultinomialNB().fit(input_vectors,output_vectors[i]))
    
    ###########################################################################
    ## SAVE COEFFICIENTS                                                      #
    ###########################################################################
    #save coefficients for use in the live run
    
    # dump the new pickles and retrain
    #coefdir = os.path.join(os.path.dirname(__file__),'coef_technique')    
    with open(os.path.join(coefdir,'coef_technique'),'wb') as f:
        pickle.dump(coef,f)               # coefficients
        pickle.dump(vocabulary,f)         # vocabulary
        pickle.dump(keys,f)               # classifications
        pickle.dump(windowsize,f)         # windowsize      
###############################################################################
# FUNCTIONS                                                                   #
###############################################################################

def build_vocab(tokenizer,text,min_freq=2):
    """
    given : tokenizer, text, min_freq(minimum frequency of a term, int)
    return: list of vocab terms
    """
    # split all text by common punct delimiters (stopword delimiters included in tokenizer)
    delimiters = u';:,\{\}\[\]\(\)\<\>\.\!\?\n\t\r`\'\\\"\*\+\/\|\^\~'
    delimiters = '|'.join(delimiters)
    strings = re.split(delimiters,text)
    strings = [x for x in strings if x is not None]
    vocab = []
    
    # collect all vocab
    for i in strings:
        vocab = vocab + tokenizer(i)
    
    # get unique >= min freq
    counts = Counter(vocab)
    out_list = [i for i in counts if counts[i]>=min_freq]
    
    # return as list of descending length unique strings
    out_list.sort(key=len,reverse=True)
    return out_list

def generate_output_vectors(listoflists):
    """
    given : a list of lists
    return: list of idx vectors to represent output vectors
    """               
    # create an idx for each sublist
    output = []
    lengths = [len(i) for i in listoflists]
    for i in xrange(len(lengths)):
        idx_start   = sum(lengths[0:i])
        idx_end     = idx_start + lengths[i]
        y_idx = np.zeros(sum(lengths),dtype=int)
        y_idx[idx_start:idx_end] = 1
        output.append(y_idx)
    return output

if __name__ == "__main__": main()