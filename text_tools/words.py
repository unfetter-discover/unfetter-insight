###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists as a repository of word-traversing functions
# punct is defined as term-delimiters common, ONLY within ASCII

# Author: William Kinsman
# Date: 2017_01_25

def prevword(text,index):
    # given: a string, index
    # return: the prev word
    if index is None: return
    return fullword(text, prevwordindex(text, index))

def nextword(text,index):
    # given: a string, index
    # return: the next word
    if index is None: return
    return fullword(text, nextwordindex(text, index))

def has_upper(text):
    # return if a string has at least one uppercase     
    if text:    
        for i in text:
            if i.isupper():
                return True
    return False

def fullword(text,index):
    # given: string, index
    # return: the full word
    # NOTE: input index MUST be an alpha
    
    # initialize
    last_index = len(text)-1
    if index is None or index < 0 or index > last_index or not text[index].isalpha():
        return
    punct = '!*\"\'()+,./`[]^;:,{}<>.?\n\t\r\\|~'
    endindex = index

    # find first letter of word
    while index != 0:
        index -= 1
        if text[index].isspace() or punct.find(text[index]) != -1:
            index += 1
            break

    # find last letter of word
    while endindex != last_index:
        endindex += 1
        if text[endindex].isspace() or punct.find(text[endindex]) != -1:
            endindex -= 1
            break
    return text[index:endindex+1]

def prevwordindex(text,index):
    # given: string, index
    # return: the starting index of previous word, else none

    # test arguments
    length = len(text)
    if index is None or index < 0 or index >= length:
        return

    # initialization
    punct = '!*\"\'()+,./`[]^;:,{}<>.?\n\t\r\\|~'
    
    # find the start of current word
    while text[index].isalpha():
        index -= 1
        if index == -1 or punct.find(text[index]) != -1:
            return

    # find end of prev word
    while index != -1 and not text[index].isalpha():
        index -= 1
        if index == -1 or punct.find(text[index]) != -1:
            return

    # find start of the prev word
    while index != -1 and text[index].isalpha():
        index -= 1
        if index == -1 or punct.find(text[index]) != -1:
            break

    # output
    return index + 1


def nextwordindex(text,index):
    # given: string, index
    # return: the starting index of next word, else none

    ## initialization
    length = len(text)
    if index is None or index < 0 or index >= length:
        return
    punct = '!*\"\'()+,./`[]^;:,{}<>.?\n\t\r\\|~'
    
    # if input is alpha find end of current word
    while text[index].isalpha():
        index += 1
        if index == length or punct.find(text[index]) != -1:
            return

    # find start of next word
    while not text[index].isalpha():
        index += 1
        if index == length or punct.find(text[index]) != -1:
            return
    return index