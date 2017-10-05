###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repository of text preprocessing functions
# These are are used to clean up a document and make it more uniform such that
# it can more easily be compared to other documents.
#
# Author: William Kinsman
# Date: 2016_12_15

import re
import numpy as np
import vocabulary
import words
from nltk.stem.porter import PorterStemmer

###############################################################################
# FUNCTIONS                                                                   #
###############################################################################    
def preprocess(text,stopwords=None):
    """
    given: a string OR list of strings, preprocess the text/s
    1) lowercase
    2) strip URLs        
    3) sub '-' for ' '
    4) change 'cmd.exe' to 'cmdDexe'; prevents unwanted splitting
        This preserves word boundaries
        This works because there should not be any capped letters anyway
    5) replace stopwords with 'SSSS' (len is avg length of stopwords)
    D=dot S=stopword
    """
    # flexible loading bool
    strbool = False
    if isinstance(text,str):
        text = [text]
        strbool = True
    
    # precompile regex
    re_url = re.compile(r'(https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})',flags=re.IGNORECASE)
    re_dotdot = re.compile(r'[\.]{2,}',flags=re.IGNORECASE)
    re_underscore = re.compile(r'\_',flags=re.IGNORECASE)
    re_dash = re.compile(r'-',flags=re.IGNORECASE)
    re_dot = re.compile(r'(?<=[a-zA-Z0-9])[.](?=[a-zA-Z])',flags=re.IGNORECASE)
    re_nonascii = re.compile(r'[^\x00-\x7F]')
    if stopwords!=None:
           sw_symbol = int(np.mean([len(word) for word in stopwords]))*'S'
           vocab_formatted = []
           for word in stopwords: vocab_formatted.append(''.join([r'\b',word,r'\b']))
           re_stopwords = re.compile('|'.join(vocab_formatted),flags=re.IGNORECASE)
           
    # perform preprocessing on all texts
    for i in range(len(text)):
        #text[i] = text[i].encode('ascii','ignore')
        text[i] = text[i].lower()                    # lowercase
        text[i] = re.sub(re_url,r' ',text[i])        # strip urls
        text[i] = re.sub(re_dotdot,r'.',text[i])     # strip extended dots
        text[i] = re.sub(re_underscore,r'U',text[i]) # replace underscores
        text[i] = re.sub(re_dash,r'',text[i])        # strip dashes
        text[i] = re.sub(re_dot,r'D',text[i])        # replace file extension dots (D)
        text[i] = re.sub(re_nonascii,r' ',text[i])   # replace all non-ascii chars with spaces

        #replace strings 
        if stopwords!=None:
               text[i] = re.sub(re_stopwords,sw_symbol,text[i]) # replace stop words (SSS) 
    
    # output
    if strbool == True:
        return text[0]
    return text
 
def stem_all(text,algo='porter'):
       """
       @param text : string or list of strings
       @param algo : snowball or porter
       @return : text with all words stemmed
       """
       # flexible loading bool (str or list of str)
       strbool = False
       if isinstance(text,str): 
              text = [text]
              strbool = True
       stemmer = PorterStemmer()
       for i in xrange(len(text)):
              # stem bodies of text (ignoring words with capped letters)
              word_starts = [m.start() for m in re.finditer(r'\b[a-zA-Z0-9]',text[i])]
              word_ends = [m.end() for m in re.finditer(r'[a-zA-Z0-9]\b',text[i])]
              for j in range(len(word_starts)-1,-1,-1):
                     word = text[i][word_starts[j]:word_ends[j]]
                     if all(x.islower() for x in word):
                            text[i] = text[i][0:word_starts[j]] + stemmer.stem(word) + text[i][word_ends[j]:len(text[i])]

       # output
       if strbool == True:
              return text[0]
       return text

def only_paragraphs(text,char_threshold=20):
    """
    @param text: text
    @param char_threshold: if paragraph has < n-chars delete it.
    return : text, only with paragraphs both over char_thresh and with a '.'
    """
    # initialize
    #regex = re.compile(r'\.(?![a-zA-Z])',flags=re.IGNORECASE)
    text = text.splitlines()
    text_new = []

    # add a paragraph if it meets all of the criteria
    for i in text:
        if '.' in i and len(i)>=char_threshold:
            text_new.append(i)
            
    # rebuild text with line returns in between 
    return '\n'.join(text_new)

def remove_reference_tags(text):
    """
    References #'s get attached to words. this damages the wiki vocab. 
    In vocab finding and training kill these.
    """
    re_ref = re.compile(r'(?<=[a-zA-Z])\d\b|(?<=[a-zA-Z])(?!32|64)\d\d\b')
    text = re.sub(re_ref,'',text)
    return text
    
def remove_false_periods(text):
    """
    given: text
    do: remove periods that are not sentance-ending
    """
    # remove periods: before is honorific/capped letter, after is capped word
    abrev_honorifics = ['amb','bgen','briggen','capt','col','dr','drs','est','gen','gov','hon','lt','jr','maj','mdme','mr','mrs','ms','msgr','prof','rep','rev','sen','sgt','sr']
    abrev_honorifics = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ') + abrev_honorifics
    regex = vocabulary.vocab_regex(abrev_honorifics,ignorecase=True)
    locs = [[x.start(),x.end(),x.group()] for x in regex.finditer(text)]
    textmax = len(text)-1

    # for each loc, kick period if followed by a capped word
    for i in xrange(len(locs)-1,-1,-1):
        if locs[i][2]<textmax and text[locs[i][2]]=='.' and words.has_upper(locs[i][2]) and words.has_upper(words.nextword(text,locs[i][1])):
            text = text[:locs[i][1]] + text[locs[i][1]+1:]
    return text