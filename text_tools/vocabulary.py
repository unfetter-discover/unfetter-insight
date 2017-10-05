###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repository of vocabulary functions

# Author: William Kinsman
# Date: 2017_04_04
import re
import numpy as np
from copy import copy

def vocab_regex(vocab,ignorecase=False):
    """
    given: a vocabulary as a list
    return: a regular expression to search for that vocabulary
    """
    assert len(vocab)==len(list(set(vocab))),(r'There are repeat terms in the vocabulary. Aborting.')
    vocab.sort(key=len,reverse=True)
    vocab_formatted = []
    for i in vocab: vocab_formatted.append(''.join([r'\b',i,r'\b']))
    if ignorecase==True:
        regex = re.compile('|'.join(vocab_formatted),flags=re.IGNORECASE)
    else:
        regex = re.compile('|'.join(vocab_formatted))
    return regex
    
def count_vectorizer(text,vocabulary):
    """
    @param text : text string
    @param vocab : list of vocab to use
    output : nparray of n rows of input vectors by m columns of vocab counts
    """
    # initialization
    assert len(vocabulary)==len(list(set(vocabulary))),(r'There are repeat terms in the vocabulary. Aborting.')
    sorted_vocab = copy(vocabulary)
    sorted_vocab.sort(key=len,reverse=True)
    vocab_idx = [vocabulary.index(i) for i in sorted_vocab] # mapping idx of decreasing length strings
    regex = vocab_regex(sorted_vocab)
    found = re.findall(regex,text)
    
    # count em up
    count = np.zeros(len(vocabulary),dtype=int)
    for i in vocab_idx:
        count[i] = found.count(vocabulary[i])
    return count