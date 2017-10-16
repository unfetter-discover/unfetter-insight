###############################################################################
# INTRODUCTION                                                                #
###############################################################################
# This module exists for extracting and handling of data from many types of
# file extensions. It also has tools for preprocessing directories, pickle
# dropping, and for searching for and grabbing files.
#
#NOTE THIS DOES NOT USE AN SSL CERT.
#
# Author: William Kinsman
# Date: 2016_12_15

###############################################################################
# IMPORTS                                                                     #
###############################################################################
import os
import re
import ssl
import urllib

# this does not use an SSL cert!!!!!
# WHY? this only done for product testing on ubuntu
try: ssl._create_default_https_context = ssl._create_unverified_context
except: pass

try:
    from textract import process
    import textract
except ImportError:
       print "You are missing the 'textract' python package. As a result, you may only parse '.txt' files."
try:
    import html2text
    from chardet import detect
except ImportError:
       print "You are missing the 'html2text' python package. As a result, you cannot parse webpages."
       
###############################################################################
# FUNCTIONS                                                                   #
###############################################################################
def list_filepaths(dirpath,nameORext=None):
    """
    @param dirpath: directory path
    @param nameORext: optionally call files by name or ext ('myfile' OR '.pdf')
    return: all of the specified filepaths in a dir (including all children)
    """
    file_paths = []
    for root, directories, files in os.walk(dirpath):
        for filetitle in files:
            filepath = os.path.join(root, filetitle)
            if nameORext and not (os.path.splitext(os.path.basename(filepath))[0] or nameORext==os.path.splitext(filepath)[1]):
                continue
            file_paths.append(filepath)
    return file_paths 
    
def extract_text(filepath):
    """
    @param path: filepath
    return : text string or false on failure
    """
    # get extension and convert accordingly, else skip it if incompatible
    if is_url(filepath):
        text = extract_web_text(filepath)
        if text == False: return False
    else:
        filename = str(filepath).split("/")[-1]
        #assert os.path.exists(filepath),('Filepath not found! Aborting. "' + filepath + '"')
        #assert os.path.isfile(filepath),('Path does not point to a file! Aborting. "' + filepath + '"')
        if filename.split('.')[-1] == "txt":
            f = open(filepath,'r')
            text = f.read()
        else:
            try:
                text = process(filepath)
                text = "".join([s for s in text.strip().splitlines(True) if s.strip()])

            except:    
                print "Conversion fail: " + filepath
                return False
    return text
    
def convert_dir2txt(dirpath,delete_bad=True):
    """
    @param dirpath: path of directorys
    @param delete_bad: deletes all non-readable txt file from the dir if True
    do : Convert all files below a directory to .txt, deletes files that fail
    """    
    # convert all files to txt
    filepaths = list_filepaths(dirpath)
    for fp in filepaths:
        text = extract_text(fp)
        if text == False:
            os.remove(fp)
        else:
            os.remove(fp)
            path = os.path.splitext(fp)[0] + '.txt'
            with open(path,'w') as f:
                f.write(text)
                f.close()

    # delete all files that failed to convert to txt
    # (Failures will occur for strange filetypes or encrypted pdfs)
    if delete_bad==True:
        files_all = set(list_filepaths(dirpath))
        files_txt = set(list_filepaths(dirpath,'.txt'))
        files_bad = files_all.symmetric_difference(files_txt)
        for i in files_bad:
            print "DELETING: " + i
            os.remove(i)

def is_url(string):
    """
    lightweight function for validating if a string is a url
    TRUE if string, and string alone, is a URL
    """
    regex = re.compile(r'(((http|ftp|https)://)|(www\.))([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?',flags=re.IGNORECASE)
    return regex.match(string)

def extract_web_text(url):
    try:
        r = urllib.urlopen(url).read()
    except:
        raise IOError('Text fetch failed. This could be due to one of the following:\n1. Bad URL\n2. Bad connection\n3. Unverified/no SSL certificate found. Aborting.')
    encoding = detect(r)['encoding']
    h = html2text.HTML2Text()
    h.ignore_links = True
    return h.handle(r.decode(encoding,'ignore'))

