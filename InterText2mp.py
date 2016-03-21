from __future__ import unicode_literals #for python2 compatibility
# -*- coding: utf-8 -*-
#created at UC Berkeley 2015
#Author: Christopher Hench ©

#This program takes ngrams of two texts, compares using fuzzywuzzy, and yields intertextualities
#Input is text and folder of texts to be compared, window of n-grams, and threshold for match 0 - 100

import os
import sys
import glob
from collections import Counter
import csv
from string import punctuation
import time
from itertools import chain
import multiprocessing
from joblib import Parallel, delayed
from fuzzywuzzy import fuzz
import re



#From NLTK Bird, Steven, Edward Loper and Ewan Klein (2009), Natural Language Processing with Python. O’Reilly Media Inc.
def ngrams(sequence, n, pad_left=False, pad_right=False, pad_symbol=None):
    sequence = iter(sequence)
    if pad_left:
        sequence = chain((pad_symbol,) * (n-1), sequence)
    if pad_right:
        sequence = chain(sequence, (pad_symbol,) * (n-1))

    history = []
    while n > 1:
        history.append(next(sequence))
        n -= 1
    for item in sequence:
        history.append(item)
        yield tuple(history)
        del history[0]


#clean text
def cleantext(text):
    text = text.lower()
    text = re.sub("[0-9]+[a-z]*", "", text)
    text = ''.join([i for i in text if i not in list(punctuation)])

    #for latin texts
    text = text.replace("v","u")
    text = text.replace("æ","ae")

    text = ' '.join(text.split())

    return (text)


#find matches above sim threshold, use for multiprocessing
def process_ngrams(i, ctri):

    matchdata = []
    cscore = 0

    for word in ctri.split():
        if (wc[word]/len(wc)) > (sens-.001):
            cscore += (sens-.001)
        else:
            cscore += (wc[word]/len(wc))

    #must meet req of most common words
    if cscore < sens:
        for j, mtri in enumerate(mtril):
            if fuzz.token_sort_ratio(ctri, mtri) > thresh and i >= window and j >= window and i < (len(ctril)-window) and j < (len(mtril)-window):

                #match grabs n-gram size on each side, for later csv writing
                match = ((ctril[i-(window)] + " " + ctri + " " + ctril[i+(window)]),
                    (mtril[j-(window)] + " " + mtri + " " + mtril[j+(window)]))
                
                d1ind = t1.find(match[0])
                d2ind = t2.find(match[1])

                matchdata.append((match[0],d1ind,match[1],d2ind))

    return matchdata


##############################################################################################################
#MAIN PROGRAM STARTS HERE

texta = sys.argv[1] #text 1
folder = sys.argv[2] # folder containing texts
window = int(sys.argv[3]) # n-gram size
thresh = int(sys.argv[4]) #fuzzywuzzy threshold, recommended 90-95 for Latin
sens = float(sys.argv[5]) #recommended .015-.02


for textb in glob.glob(folder+'/*'):
    
    #get names for printing purposes
    f1name = (texta.split("/")[-1]).split(".")[0]
    f2name = (textb.split("/")[-1]).split(".")[0]

    print("\nProcessing " + f1name + " and " + f2name)

    #open files
    with open(texta, 'r', encoding='utf-8') as f:
        text1 = f.read()

    with open(textb, 'r', encoding='utf-8') as f:
        text2 = f.read()

    d1len = len(text1)
    d2len = len(text2)

    #clean texts
    t1 = cleantext(text1)
    t2 = cleantext(text2)

    #find word counts
    c1 = Counter(t1.split())
    m1 = Counter(t2.split())
    c1.update(m1)
    wc=c1

    #create n-grams
    print ("Finding "+str(window)+"-grams...")
    ctris = list(ngrams(t1.split(), window))
    mtris = list(ngrams(t2.split(), window))

    #rejoin n-grams for string comparison
    ctril = [" ".join(tri) for tri in ctris]
    mtril = [" ".join(tri) for tri in mtris]

    tlen = len(ctril)

    print ("Looking for intertextuality...")
    print ("Starting at: "+time.strftime("%H:%M:%S"))

    #start multiprocessing
    num_core = multiprocessing.cpu_count()
    matchdata = Parallel(n_jobs=num_core)(delayed(process_ngrams)(i, ctri) for i, ctri in enumerate(ctril))
    
    #clean up after multiprocessing
    matchdata = [x[0] for x in matchdata if len(x) != 0]

    #take out matches of close proximity (e.g. same sentence)
    newmatches = []
    for i,v in enumerate(matchdata):
        if i == 0:
            newmatches.append(v)
        elif i > 0 and v[1] > (matchdata[i-1][1] + len(matchdata[i-1][0])):
            newmatches.append(v)
        else:
            continue


    print ("Finished searching at: "+time.strftime("%H:%M:%S"))

    print ("Found " + str(len(newmatches)) + " intertexualities")

    print ("\nWriting...")

    if not os.path.exists("InterTextResults"): #folder to collect results
        os.makedirs("InterTextResults")

    #save results to csv
    with open("InterTextResults/intertext.csv", 'a') as f:
                writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
                writer.writerow([f1name, f1name + " Loc", f2name, f2name + " Loc"])
                for data in newmatches:
                    writer.writerow(data)
                writer.writerow([""])

    #write html output
    ntext1 = t1
    ntext2 = t2
    alinks = ''
    blinks = ''
    for i, item in enumerate(newmatches):

        alinks += '<a href="#intta'+str(i)+'"> ['+str(i)+']</a>'
        blinks += '<a href="#inttb'+str(i)+'"> ['+str(i)+']</a>'

        pos = ntext1.find(item[0])
        if pos != -1:
            ntext1 = ntext1[:pos] + '<a name="intta'+str(i)+'"></a><h4 style="color:red;">(' + str(i) + ") " + ntext1[pos:pos+len(item[0])]+ '<a href="#inttb'+str(i)+'"> ('+f2name+')</a></h4>' + ntext1[pos+len(item[0]):]

        pos = ntext2.find(item[2])
        if pos != -1:
            ntext2 = ntext2[:pos] + '<a name="inttb'+str(i)+'"></a><h4 style="color:red;">(' + str(i) + ") " + ntext2[pos:pos+len(item[2])]+ '<a href="#intta'+str(i)+'"> ('+f1name+')</a></h4>' + ntext2[pos+len(item[2]):]


    html = '''<style type="text/css">
    #wrap {
       width:800px;
       margin:0 auto;
    }
    #left_col {
       float:left;
       width:350px;
    }
    #right_col {
       float:right;
       width:350px;
    }
    #header {
      text-align:center;
      padding:5px;
    }
    </style>

<div id="header">
<h1>Inter Text v 0.1</h1>
<p>'''+f1name.upper()+': '+alinks+'''</p>
<p>'''+f2name.upper()+': '+blinks+'''</p>
</div>

    <div id="wrap">
        <div id="left_col">
            <h2>'''+f1name.upper() + '''</h2>'''+ntext1+'''
        </div>
        <div id="right_col">
            <h2>'''+f2name.upper() + '''</h2>'''+ntext2+'''
                </div>
    </div>'''


    with open ("InterTextResults/"+f1name+" "+f2name+".html", 'w') as f:
        f.write(html)

    print ("\nResults saved to 'intertext.csv' .\n")

