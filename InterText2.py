'''Program to find intertextualities between two texts. Algorithm uses
fuzzywuzzy string matching and special doublet hashing by Zach Schollz
https://github.com/schollz/string_matching in order to lookup fuzzy matches.
This program thus accounts for differing orthography or case/syntactic
variation with the threshold parameter. '''

import re
from string import punctuation
from collections import Counter
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import Levenshtein
import operator
from multiprocessing import Pool
from collections import Counter
import pyprind
import sys
from write_to_html import write_to_html


def compareStrings(strings):
    '''Compute degree of match'''

    leven1 = fuzz.token_set_ratio(strings[0], strings[1])
    leven2 = Levenshtein.ratio(str(strings[0]), str(strings[1]))
    return (strings[0], strings[1], leven1 + leven2 * 100, leven2)


def searchThroughList(searchString, listOfStrings):
    '''Search for matches in list of strings (the collisions
    form the hash table)'''

    stringList = []
    for string in listOfStrings:
        stringList.append((searchString.lower(), string.lower()))

    pool2 = Pool(2)
    results = pool2.map(compareStrings, stringList)
    pool2.close()
    pool2.join()
    finalResult = [it for it in (sorted(results, key=operator.itemgetter(2, 3),
                   reverse=True)) if it[2] > thresh]

    if len(finalResult) > 0:
        return listOfStrings[[x.lower() for x in
                              listOfStrings].index(finalResult[0][1])]
    else:
        return False


def generateSearchableHashFromList(listOfStrings):
    '''Create hash table from all strings using doublets'''

    sHash = {}
    for string in listOfStrings:
        for i in range(0, len(string) - 2):
            doublet = string[i:i + 3].lower()
            if doublet not in sHash:
                sHash[doublet] = []
            sHash[doublet].append(string)
    return sHash


def searchThroughHash(searchString, sHash, listOfStrings):
    '''Search through hash table for string and yield list
    of possible strings'''

    searchString = searchString.lower()
    possibleStrings = []
    for i in range(0, len(searchString) - 2):
        doublet = searchString[i:i + 3]
        if doublet in sHash:
            possibleStrings += sHash[doublet]
    c = Counter(possibleStrings)
    mostPossible = []
    for p in c.most_common(1000):
        mostPossible.append(p[0])
    return searchThroughList(searchString, mostPossible)


# From NLTK Bird, Steven, Edward Loper and Ewan Klein (2009), Natural
# Language Processing with Python. O’Reilly Media Inc.
def ngrams(sequence, n, pad_left=False, pad_right=False, pad_symbol=None):
    '''Create sequence of n-grams for words'''

    sequence = iter(sequence)
    if pad_left:
        sequence = chain((pad_symbol,) * (n - 1), sequence)
    if pad_right:
        sequence = chain(sequence, (pad_symbol,) * (n - 1))

    history = []
    while n > 1:
        history.append(next(sequence))
        n -= 1
    for item in sequence:
        history.append(item)
        yield tuple(history)
        del history[0]


# clean text
def cleantext(text):
    '''Clean input texts'''

    text = text.lower()
    text = re.sub("[0-9]+[a-z]*", "", text)
    text = ''.join([i for i in text if i not in list(punctuation)])

    # for latin texts
    text = text.replace("v", "u").replace("æ", "ae")
    text = ' '.join(text.split())

    return text

if __name__ == "__main__":
    # main program starts here
    text_1_path = sys.argv[1]
    text_2_path = sys.argv[2]
    window = int(sys.argv[3])  # recommended 3
    thresh = int(sys.argv[4])  # recommended 195
    print()

    with open(text_2_path, "r") as f:
        raw_text2 = f.read()

    clean_text2 = cleantext(raw_text2)
    text2_words = clean_text2.split()

    # create n-grams
    tris_text2 = list(ngrams(text2_words, window))

    new_dict = {}
    sorted_tris_text2 = []
    # rejoin n-grams for string comparison
    for i, tri in enumerate(tris_text2):
        sorted_t = "".join(sorted("".join(tri)))
        reg_t = "".join(tri)
        new_dict[sorted_t] = i
        sorted_tris_text2.append(sorted_t)

    hashes2 = generateSearchableHashFromList(sorted_tris_text2)

    # TEXT 1
    with open(text_1_path, "r") as f:
        raw_text1 = f.read()

    clean_text1 = cleantext(raw_text1)
    text1_words = clean_text1.split()

    # create n-grams
    tris_text1 = list(ngrams(text1_words, window))

    new_dict1 = {}
    sorted_tris_text1 = []

    # rejoin n-grams for string comparison
    for i, tri in enumerate(tris_text1):
        sorted_t = "".join(sorted("".join(tri)))
        reg_t = "".join(tri)
        new_dict1[sorted_t] = i
        sorted_tris_text1.append(sorted_t)

    bar = pyprind.ProgBar(len(sorted_tris_text1), monitor=True, bar_char="#")
    collected_matches = []
    for t in sorted_tris_text1:
        a = searchThroughHash(t, hashes2, sorted_tris_text2)
        if a:
            collected_matches.append((tris_text2[new_dict[a]],
                                     tris_text1[new_dict1[t]]))
        bar.update()
    print(bar)
    print()

    print(str(len(collected_matches)) + " matches found:")
    for i, m in enumerate(collected_matches):
        print(i+1, m)

    write_to_html(collected_matches, clean_text1, clean_text2)

    print()
