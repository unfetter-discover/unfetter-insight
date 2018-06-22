###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repository of text convolution functions
# These are are used to for a number of reasons including:
# 1: busting up a document into windowsizes for creating more discrete samples
# 2: determining the continuity of a phrase, string or vocabulary in a text
# 3: determining the continuity of a phrase relative to others
# 4: and a lot more!

# NOTE: we assume that all strings loaded are unicode strings

# Author: William Kinsman
# Date: 2017_01_25

###############################################################################
# IMPORTS                                                                     #
###############################################################################
import re
import numpy as np
from numpy.matlib import repmat
from functools import partial
from tqdm import tqdm
from multiprocessing import cpu_count,Pool
###############################################################################
# FUNCTIONS                                                                   #
###############################################################################

def tf_vectorizer(texts,vocabulary,idf=None,parallel=False):
    """
    @param texts : list of texts
    @param vocab : list of vocab to use
    @param idf : np vector, if passed is applied to all input vectors
    @param parallel : if true, autodetects and uses all cores in parallel
    output : nparray of n rows of input vectors by m columns of vocab TF(IDF)'s
    DISCLOSURE: if building a convoluded 2+ngram, this function will
    improperly detect partial portions only of n-grams near the fence
    """
    # initialization
    assert len(vocabulary)==len(list(set(vocabulary))),(r'There are repeat terms in the vocabulary. Aborting.')
    input_vectors = np.zeros((len(texts),len(vocabulary)))
    sorted_vocab = vocabulary
    sorted_vocab.sort(key=len,reverse=True)
    vocab_idx = [vocabulary.index(i) for i in sorted_vocab] # mapping idx of decreasing length strings
    
    # create the regular expression
    vocab_formatted = []
    for i in vocab_idx: vocab_formatted.append(''.join([r'\b',vocabulary[i],r'\b']))
    regex = re.compile('|'.join(vocab_formatted))
    
    # parallel case
    if parallel == True:
        pool = Pool(processes=cpu_count())
        function = partial(_tf,vocabulary,vocab_idx,regex)
        vectors = pool.map(function,texts)
        pool.close()
        pool.join()
        for i in xrange(len(texts)):
            input_vectors[i,:] = vectors[i]
    
    # serial case
    else:
        vectors = []
        for i in tqdm(xrange(len(texts))):
            input_vectors[i,:] = _tf(vocabulary,vocab_idx,regex,texts[i])
    
    # apply idf if provided
    if not idf is None:
        assert(len(idf)==len(vocabulary)),("IDF vector dimensions do not match vocabulary size. Aborting.")
        idf = repmat(idf,len(input_vectors),1)
        input_vectors = np.multiply(input_vectors,idf)
        
    return input_vectors
    
def _tf(vocab,vocab_idx,regex,text):
    
    # fetch all locations
    found = re.findall(regex,text)
    
    # slide into the counts
    count = np.zeros(len(vocab))
    for i in vocab_idx:
        count[i] = found.count(vocab[i])
    
    #perform SKL transform supress /0 errors (nan->0)
    with np.errstate(divide='ignore',invalid='ignore'):
           squared = np.square(count)
           out = np.nan_to_num(np.sqrt(squared/float(np.sum(squared))))
    return out

def idf_vector(texts,vocabulary):
    """
    given a corpus and a vocab, return an idf vector
    """
    # initialization
    assert len(vocabulary)==len(list(set(vocabulary))),(r'There are repeat terms in the vocabulary')
    idf = np.zeros(len(vocabulary))
    sorted_vocab = vocabulary
    sorted_vocab.sort(key=len,reverse=True)
    vocab_idx = [vocabulary.index(i) for i in sorted_vocab] # mapping idx of decreasing length strings
    N = len(texts)
                 
    # create the regular expression
    vocab_formatted = []
    for i in vocab_idx: vocab_formatted.append(''.join([r'\b',vocabulary[i],r'\b']))
    regex = re.compile('|'.join(vocab_formatted))
    
    for i in xrange(len(texts)):
        found = set(re.findall(regex,texts[i]))
        for j in vocab_idx:
            if vocabulary[j] in found:
                idf[j] = idf[j] + 1
    idf = np.log(float(N+1)/(idf+1))+1
    return idf


def convolve_text(text,windowsize=400,step=50,ws_trim=False,word_trim=True,fence=False,return_ci=False):
    """
    @param text : some text
    @param windowsize : character size of text window (unicode chars = 1)
    @param step : defines how many characters are stepped each run (speed)
    @param ws_trim : if true truncates whitespace
    @param word_trim : if true truncates to word boundaries (will slow run)
    @param fence : if true includes fence conditions of sliding window
    @param return_ci : optionally return the center index of each window
    NOTE: this function does NOT perform preprocessing of vocab or text!
    """
    # initialization
    if len(text)<=windowsize:
        if return_ci==True:
            return [text],[len(text)/2]
        else:
            return [text]

    # create list of obvious ranges
    text_len = len(text)
    strings = [[i,i+windowsize] for i in xrange(0,text_len-(windowsize-1),step)]
    
    # optionally add fence condition ranges
    if fence == True:
        
        #starting fence
        strings = [[0,i] for i in xrange(1,windowsize)] + strings
                             
        #ending fence
        strings = strings + [[text_len-i,text_len] for i in xrange(windowsize,0,-1)]
    
    # optionally check word boundaries
    if word_trim == True:
        ws_trim = True
        word_starts = [m.start() for m in re.finditer(r'\b[a-zA-Z0-9]',text)]
        word_ends = [m.end() for m in re.finditer(r'[a-zA-Z0-9]\b',text)]
        
        # check starting boundary, else find next starting bound
        i = 0
        while i < len(strings):
            while strings[i][0] not in word_starts and strings[i][0]<strings[i][1]:
                strings[i][0] += 1
            if strings[i][0]==strings[i][1]:
                del strings[i]
                continue
            i += 1
                    
        # check ending boundary, else step back to an ending bound
        i = 0
        while i < len(strings):
            while strings[i][1] not in word_ends and strings[i][1]>strings[i][0]:
                strings[i][1] -= 1
            if strings[i][0]==strings[i][1]:
                del strings[i]
                continue
            i += 1
        
        # eliminate repeats
        if len(strings)>1:
            for i in xrange(len(strings)):
                while i<len(strings)-1 and strings[i]==strings[i+1]:
                    del strings[i+1]
    
    # add all unique strings/ci to the output list
    ci = []
    text_strings = []
    for i in xrange(len(strings)):
        text_block = text[strings[i][0]:strings[i][1]]
        if ws_trim==True: text_block = text_block.strip()   #strip ws if called
        if text_block not in text_strings:
            ci.append((strings[i][1]-strings[i][0])/2.+strings[i][0])
            text_strings.append(text_block)
    
    #optionally return center index
    if return_ci==True:
        return text_strings,ci
    return text_strings
    
def strip_low_info_convolutions(convolutions,vocab,min_vocab=10):
    """
    @param convolutions : list of texts generated from text convolution
    @param vocab : list of vocab to use
    @param min_vocab : minimum number of unique terms in vocab required in text
    @return convolutions, but without low-vocab texts
    """
    # build regex
    vocab.sort(key=len,reverse=True)
    vocab_formatted = []
    for i in xrange(len(vocab)): vocab_formatted.append(''.join([r'\b',vocab[i],r'\b']))
    regex = re.compile('|'.join(vocab_formatted))
 
    # count number of unique vocab terms present
    for i in xrange(len(convolutions)):
        if len(set(re.findall(regex,convolutions[i])))<min_vocab:
            convolutions[i] = ''
    return convolutions
    
