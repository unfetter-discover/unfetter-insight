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
from copy import copy
from tqdm import tqdm
from functools import partial
from multiprocessing import cpu_count,Pool
###############################################################################
# FUNCTIONS                                                                   #
###############################################################################

def convolved_text_vectorizer(text,vocabulary,windowsize=500,step=50,fence=False,return_ci=False,parallel=False):
    """
    @param text : some text
    @param windowsize : character size of text window (unicode chars = 1)
    @param step : defines how many characters are stepped each run (speed)
    @param fence : if true includes fence conditions of sliding window
    @param return_ci : optionally return the center index of each window
    NOTE: this function does NOT perform preprocessing of vocab or text!
    """
    # initialization
    if len(text)<=windowsize: windowsize = len(text)

    # index vocab locations
    assert len(vocabulary)==len(list(set(vocabulary))),(r'There are repeat terms in the vocabulary. Aborting.')
    sorted_vocab = copy(vocabulary)
    sorted_vocab.sort(key=len,reverse=True)
    vocab_idx = [vocabulary.index(i) for i in sorted_vocab] # mapping idx of decreasing length strings
    vocab_formatted = []
    for i in vocab_idx: vocab_formatted.append(''.join([r'\b',vocabulary[i],r'\b']))
    regex = re.compile('|'.join(vocab_formatted))

    # create list of obvious ranges and optionally add fence conditions
    text_len = len(text)
    strings = [[i,i+windowsize] for i in xrange(0,text_len-(windowsize-1),step)]
    if fence == True:
        strings = [[0,i] for i in xrange(1,windowsize)] + strings
        strings = strings + [[text_len-i,text_len] for i in xrange(windowsize,0,-1)]
    
    # for each string range, build a count vector of vocab terms entirely in window
    input_vectors = np.zeros((len(strings),len(vocabulary)))
    vocab_found = [(i.start(), i.end(), i.group()) for i in regex.finditer(text)]
           
    # parallel case
    if parallel == True:
        pool = Pool(processes=cpu_count())
        function = partial(_tf,vocabulary,vocab_idx,vocab_found)
        vectors = pool.map(function,strings)
        pool.close()
        pool.join()
        for i in xrange(len(strings)):
            input_vectors[i,:] = vectors[i]
    
    # serial case
    else:
        vectors = []
        for i in tqdm(xrange(len(strings))):
            input_vectors[i,:] = _tf(vocabulary,vocab_idx,vocab_found,strings[i])
    
    # output
    if return_ci:
        ci = [(i[1]-i[0])/2 for i in strings]
        return input_vectors,ci
    return input_vectors

def _tf(vocab,vocab_idx,vocab_found,string_range):
    # count relevant words that fall in window
    words = [tup[2] for tup in vocab_found if tup[0]>=string_range[0] and tup[1]<=string_range[1]] 
    
    # slide into the counts
    count = np.zeros(len(vocab))
    for j in vocab_idx:
        count[j] = words.count(vocab[j])
    
    #perform SKL transform supress /0 errors (nan->0)
    with np.errstate(divide='ignore',invalid='ignore'):
           squared = np.square(count)
           count = np.nan_to_num(np.sqrt(squared/float(np.sum(squared))))
    return count
    
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