# slugify lists built in excel!
# slugified strings can be used as variables
# this could use a new slugification algo that allows for slug reversing

from slugify import slugify

def slugify_list(string):
    """
    given: a single string with \n delimiters
    return: a slugified list of strings
    1) copy data to clipboard from excel
    2) paste into a variable
    3) run this script on it
    """
    string = unicode(string)
    string = string.split('\n')
    for i in xrange(len(string)): slugify(string[i])
    string = filter(None, string)
    if list(set(string))!=string:
        print 'NOTE: There is a repeat string in the list!'
    return string
