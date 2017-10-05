
import os
import matplotlib.pyplot as plt
from chardet import detect
from nltk import word_tokenize

def text_similarity(textA,textB):
    """
    @param textA: 1st body of text (unicode)
    @param textB: 2nd body of text (unicode)
    note:   uses token jaccard distance returning a decimal percent
    """
    # NLTK VERSION (SPACY equivelent created, was same speed; try Cython?)
    textA = set(word_tokenize(textA))
    textB = set(word_tokenize(textB))    
    intersection = len(textA.intersection(textB))
    difference = len(textA.symmetric_difference(textB))
    similarity = intersection/float(intersection+difference)  
    print "Text similarity: " + str(similarity)
    return similarity
    
    
def fetch_unique(dirpath):
    """
    @param source_dir: dir of text files
    return: list of (filepath,text) of unique files
    """
    # initialize (filepaths and texts)
    fp = [f for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath,f))]
    x = []
    y = []

    # create an input(x) and output(y) for each filepath
    for i in range(len(fp)):

        # generate x value (contents of the text file)
        with open(fp[i],'r') as f:
            text = f.read()
            if not text: 
                print 'No text in: ' + fp[i]
                del fp[i]
                continue
            else:
                encoding = detect(text)['encoding']
                text = text.decode(encoding)
                x.append(text)

        # generate y value (bin the text file belongs to)
        y.append(set([os.path.basename(os.path.dirname(fp[i]))]))

    # Do a combinatory comparison to see if any belong to other bins. If so, merge.
    # this can be sped up by not comparing within the same directory
    histogram_data = []
    i = 0
    while i < len(fp):
        textA = x[i]
        j = i + 1
        while j < len(fp):
            textB = x[j]

            # IF texts are the same, merge bins into the i'th iteration
            similarity = text_similarity(textA,textB)
            histogram_data.append(similarity)
            if similarity >.5:
                y[i].update(y[j]) # add the bin to i's bin list
                del y[j]
                del x[j]
                del fp[j]
            else:
                j += 1
        i += 1
    
    # print results of similarity measures for verifying performance
    plt.hist(histogram_data,bins=30,range=[0,1])
    plt.title("Similarities")
    plt.xlabel("Similarity")
    plt.ylabel("Count")
    
    # convert all text strings(x) to utf-8 and sets(y) back to lists
    assert len(x)==len(y)==len(fp)
    for i in range(len(x)): 
        x[i] = x[i].encode('utf-8')
        y[i] = list(y[i])
        y[i].sort()
    categories = list(set([item for sublist in y for item in sublist]))
    categories.sort()
    return fp,x,y,categories