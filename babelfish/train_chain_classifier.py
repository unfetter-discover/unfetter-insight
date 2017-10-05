###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# Attempt at chain classification
# This attempt uses 1vsAll of a chains categories
# Author: William Kinsman
# Date: 2016_02_24
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
from text_tools.preprocessing import preprocess, remove_reference_tags, stem_all
from text_tools.convolution import convolve_text,tf_vectorizer
###############################################################################
# DATA LOADING                                                                #
###############################################################################
def main():

       ###########################################################################
       # MODEL CUSTOMIZATIONS                                                    #
       ###########################################################################
       min_ngram_freq = 3              # min freq required to be added to vocab (2 slightly better, but much longer runtime)
       max_ngram = 1                   # max number of words allowed in a vocab term
       regex = r'\b([A-Za-z]{3,}|[0-9]+[A-Za-z]{2,}|[A-Za-z]{2,}[0-9]+|[A-Za-z]+[0-9]+[A-Za-z]+)\b'  # regex defining acceptable n-gram words (alphanumeric, but NOT numeric)
       windowsize = 500                # character size of the sliding window.
       step = 1                        # number of characters to step per slide.
       parallel = False                # run training in parallel?
       more_stopwords = ['like','use','uses','used','using','able','aid','aids'] # additional stopwords beyond standard
       stopwords = list(STOPWORDS.ENGLISH_STOP_WORDS.union(more_stopwords))
       
       ###########################################################################
       # CONSTRUCT CONVOLUTIONS AND VOCABULARY                                   #
       ###########################################################################
       # build tokenizer
       tokenizer = CountVectorizer(encoding='utf-8',decode_error='ignore',lowercase=False,ngram_range=(1,max_ngram),token_pattern=regex,stop_words=stopwords)
       tokenizer = tokenizer.build_analyzer()
       
       dir_sp = sys.path
       coefdir = None
       for i in range(len(dir_sp)):
           if os.path.isdir(os.path.join(dir_sp[i],'babelfish')):
               coefdir = os.path.join(dir_sp[i],'babelfish')
               break
       assert coefdir!=None, "Could not locate site-packages directory with babelfish. Aborting." 
       
       # load training data
       with open(os.path.join(coefdir,'dict_wiki')) as f:
           wiki_dict = pickle.load(f)  # wiki texts
       with open(os.path.join(coefdir,'dict_attackchain')) as f:
           attack_chains_dict = pickle.load(f)
           attack_chain_texts = attack_chains_dict.keys()
       
       # preprocess text and build vocabulary    
       processed = []
       convolutions = []
       for key in wiki_dict:
           text = preprocess(wiki_dict.get(key))
           text = remove_reference_tags(text)
           text = stem_all(text)
           processed.append(text)
           text = convolve_text(text,windowsize=windowsize,step=step,ws_trim=False,word_trim=True,fence=False)
           convolutions.append(text)
           wiki_dict[key] = text
       all_text = '\n'.join(processed)
       vocabulary = build_vocab(tokenizer,all_text,min_ngram_freq)
       
       # for each attack chain element
       for i in xrange(len(attack_chain_texts)):
           techs = attack_chains_dict[attack_chain_texts[i]]
           attack_chain_texts[i] = []
           
           # get text convolutions for each method used
           for j in techs:
               if j not in wiki_dict.keys(): continue
               attack_chain_texts[i] = attack_chain_texts[i] + wiki_dict[j]
       
       ###########################################################################
       # TRAINING                                                                #
       ###########################################################################
       all_convolutions = [item for sublist in attack_chain_texts for item in sublist]
       input_vectors = tf_vectorizer(all_convolutions,vocabulary,parallel=parallel)
       y_idx = generate_output_vectors(attack_chain_texts)
       
       # build coefficients for each classifier
       coef = []
       for i in xrange(len(attack_chains_dict)):
           coef.append(MultinomialNB().fit(input_vectors,y_idx[i]))
       
       ###########################################################################
       ## SAVE COEFFICIENTS                                                      #
       ###########################################################################
       #save coefficients for use in the live run
       #dump the new pickles and retrain
       #coefpath = os.path.join(os.path.dirname(__file__),'coef_chain')      
       with open(os.path.join(coefdir,'coef_chain'),'wb') as f:
           pickle.dump(coef,f)               # coefficients
           pickle.dump(vocabulary,f)         # vocabulary
           pickle.dump(attack_chains_dict.keys(),f)   # classifications
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
    delimiters=u';:,\{\}\[\]\(\)\<\>\.\!\?\n\t\r`\'\\\"'
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