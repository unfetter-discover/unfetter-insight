###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repository of ENGLISH entity resolution functions
# These are used to detect the main proper nouns over the course of a document

# Author: William Kinsman
# Date: 2017_04_06

# ISSUES:
# error handling for 'Bob and Tom'
# error handling for 'Bob, Tom, and Jerry'
#0. When 'Hi-Bob' is found it looks for all locations of 'Hi Bob' instead
#1. all capped terms not accepted? this is ok, but why happening?
#2. nicknames resolved
import re
import numpy as np
from sklearn.feature_extraction import text as STOPWORDS
from scipy.optimize import curve_fit
from scipy.misc import derivative

# local to text_tools
import text_tools.words
import text_tools.preprocessing
import text_tools.vocabulary

def entity_resolution(text,max_words=5,factor=None):
    
    # preprocessing
    text = text_tools.preprocessing.remove_false_periods(text)
    
    # build proper noun pool
    nameDict = build_name_dict(text,max_words)
    if len(nameDict)==0: return None
    
    # merge names by nicknames
    return nameDict

    # only get the top entities
    merged = [(k,len(v['locs'])) for k,v in nameDict.iteritems()]
    counts = [i[1] for i in merged] 
    if len(merged)==1: return merged
    if factor:
        min_count = hist_decay_point(counts,factor)
        merged = [i for i in merged if i[1]>=min_count]
    
    merged = sorted(merged, key=lambda x: x[1], reverse=True)
    return merged


def build_name_dict(text,max_words=5):
    names = find_capped_chains(text)
    names = [name for name in names if len(name.split())<=max_words]
    #initiate dictionary: add names and unique locations
    names.sort(key=len,reverse=True)
    regex = text_tools.vocabulary.vocab_regex(names)
    locs = [(i.start(),i.end(),i.group()) for i in regex.finditer(text)]
    namesDict = {name: {'aliases':[name],'sex': None,'locs':[]} for name in names}
    for k,v in namesDict.iteritems():
        v['locs'] = [(i[0],i[1]) for i in locs if i[2]==k]
    return namesDict


def find_capped_chains(text):
    """
    given: text
    return: all strings of capped words; head/tail may not be stopwords/nums
    """
    # get all non-stopword capped alphanumerics
    regex = re.compile(r'\b[A-Z]+[a-z0-9]+\b') 
    phrases = [[i.start(),i.end(),i.group()] for i in regex.finditer(text)]
    i=0
    while i < len(phrases):
        word = phrases[i][2].lower()
        if len(word)==1 or word in STOPWORDS.ENGLISH_STOP_WORDS : 
            del phrases[i]
        else:
            i+=1
    
    # for EA phrase, step back to prevword; uncapped words/punct as delimiters
    for phrase in phrases:
        new_word = True
        while new_word:
            new_word_idx = text_tools.words.prevwordindex(text,phrase[0])
            new_word = text_tools.words.fullword(text,new_word_idx)
            if new_word==None or text_tools.words.has_upper(new_word)==False:
                break
            else:
                phrase[0] = new_word_idx
                phrase[2] = text[phrase[0]:phrase[1]]
    
    # delete similar instances
    i=0
    while i < len(phrases)-1:
        if phrases[i][0]==phrases[i+1][0]:
            del phrases[i]
        else:
            i+=1
    
    # strip metadata (no longer need it)
    phrases = [x[2] for x in phrases]

    # remove first word while starting with num or startwords
    i=0
    while i < len(phrases):
        word = phrases[i].split()
        if len(word)==1:
            i+=1
            continue # shortcircuit
        while len(word)>0 and (word[0].isdigit() or word[0].lower() in STOPWORDS.ENGLISH_STOP_WORDS):
            del word[0]
        if len(word)==0: 
            del phrases[i]
        else:
            phrases[i]=' '.join(word)
            i+=1
    
    # strip index metadata
    phrases = list(set(phrases))
    phrases.sort()
    return phrases

def hist_decay_point(vector,factor=-1):
    """
    @param : vector (must be a list, not numpy)
    @param : -99999<=x<0 or None. derivative value to seek the index of
    return: elbow point of frequecies (when deriv = factor)
    """
    if factor == None: return 0
    if type(vector) is np.ndarray: vector = np.array(vector).tolist()
    
    #count frequency of each number
    x = list(set(vector))
    y = [vector.count(i) for i in x]
    coefs,_ = curve_fit(lambda t,a,b: a*np.exp(b*t),  x,  y,  p0=(4, 0.1), maxfev=100000)
    def func(x,a=coefs[0],b=coefs[1]): return a*x**b
    derivs_range = range(1,max(x))
    derivs = [derivative(func,j) for j in derivs_range]
    
    # return count closest to desired
    return min(derivs_range[derivs.index(min(derivs, key=lambda x:abs(x-factor)))],max(x))






    