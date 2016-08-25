'''
Program to find intertextualities between two texts. Algorithm uses
fuzzywuzzy string matching and special doublet hashing by Zach Schollz
https://github.com/schollz/string_matching in order to lookup fuzzy matches.
This program thus accounts for differing orthography or case/syntactic
variation with the threshold parameter.

Author = Christopher Hench
License = MIT
'''

import re
from string import punctuation
from collections import Counter
from fuzzywuzzy import fuzz
import operator
from collections import Counter
import pyprind
import sys
# from write_to_html import write_to_html


def scoreWord(word, counter_dict):
    ranks = [x[0] for x in counter_dict.most_common()]
    singles = len([x for x in counter_dict.most_common() if x[1] == 1])
    unique_words = len(ranks)
    tail_singles = unique_words - singles

    score = 0

    if word in ranks[-singles:]:
        score += 10

    elif word in ranks[int(-singles * 1.2):]:
        score += 5

    elif word in ranks[int(-singles * 1.3):]:
        score += 4

    elif word in ranks[int(-singles * 1.4):]:
        score += 3

    elif word in ranks[int(-singles * 1.5):]:
        score += 2

    return score


def compareStrings(strings):
    '''
    Compute degree of match
    '''

    leven1 = fuzz.ratio(strings[0], strings[1])

    #leven1 = Levenshtein.ratio(strings[0], strings[1])
    return (strings[0], strings[1], leven1)


def searchThroughList(searchString, listOfStrings):
    '''
    Search for matches in list of strings (the collisions
    form the hash table)
    '''

    stringList = []
    for string in listOfStrings:
        stringList.append((searchString.lower(), string.lower()))

    results = [compareStrings(s) for s in stringList]
    finalResult = [it for it in (sorted(results, key=lambda x: x[1],
                                        reverse=True)) if it[2] > thresh]

    if len(finalResult) > 0:
        return listOfStrings[[x.lower() for x in
                              listOfStrings].index(finalResult[0][1])]
    else:
        return False


def generateSearchableHashFromList(listOfStrings):
    '''
    Create hash table from all strings using doublets
    '''

    sHash = {}
    for string in listOfStrings:
        for i in range(0, len(string) - 2):
            doublet = string[i:i + 3].lower()
            if doublet not in sHash:
                sHash[doublet] = []
            sHash[doublet].append(string)
    return sHash


def searchThroughHash(searchString, sHash, listOfStrings):
    '''
    Search through hash table for string and yield list
    of possible strings
    '''

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
    '''
    Create sequence of n-grams for words
    '''

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


def cleanText(text):
    '''
    Clean input texts
    '''
    from string import punctuation

    for char in punctuation:
        text = text.replace(char, "")

    return text


# main program
if __name__ == "__main__":

    text_1_path = sys.argv[1]
    f1name = text_1_path.split("/")[-1].split(".")[0]
    text_2_path = sys.argv[2]
    f2name = text_2_path.split("/")[-1].split(".")[0]

    window = int(sys.argv[3])  # recommended 3
    thresh = float(sys.argv[4])  # recommended 85
    print()

    # TEXT 2
    with open(text_2_path, "r") as f:
        raw_text2 = f.read()

    clean_text2 = cleanText(raw_text2)
    text2_words = clean_text2.split()

    # create n-grams
    tris_text2 = list(ngrams(text2_words, window))

    new_dict2 = {}
    j_tris_text2 = []
    # rejoin n-grams for string comparison
    for i, tri in enumerate(tris_text2):
        j_t = "".join(sorted(tri))
        new_dict2[j_t] = i
        j_tris_text2.append(j_t)

    hashes2 = generateSearchableHashFromList(j_tris_text2)

    # TEXT 1
    with open(text_1_path, "r") as f:
        raw_text1 = f.read()

    clean_text1 = cleanText(raw_text1)
    text1_words = clean_text1.split()

    all_words = text1_words + text2_words
    all_words_freq = Counter(all_words)

    # create n-grams
    tris_text1 = list(ngrams(text1_words, window))

    new_dict1 = {}
    j_tris_text1 = []
    # rejoin n-grams for string comparison
    for i, tri in enumerate(tris_text1):
        j_t = "".join(sorted(tri))
        new_dict1[j_t] = i
        j_tris_text1.append(j_t)

    # create hash table for text 2 (the one to compare to)
    hashes2 = generateSearchableHashFromList(j_tris_text2)

    print("Looking for matches...")
    bar = pyprind.ProgBar(len(j_tris_text1), monitor=True, bar_char="#")
    collected_matches = []
    for t in j_tris_text1:
        a = searchThroughHash(t, hashes2, j_tris_text2)
        if a:
            collected_matches.append((tris_text2[new_dict2[a]],
                                      tris_text1[new_dict1[t]]))
        bar.update()

    print()

    print("Scoring matches...")
    bar = pyprind.ProgBar(len(collected_matches), monitor=True, bar_char="#")
    sifted_matches = []
    for i, m in enumerate(collected_matches):
        tri_score = sum(
            [scoreWord(word, all_words_freq) for word in m[1]])
        if tri_score > 2:
            sifted_matches.append((m, tri_score))

        bar.update()

    print()

    sifted_matches = set(sifted_matches)

    print(str(len(sifted_matches)) + " matches found:")
    for i, m in enumerate(sifted_matches):
        print(i + 1, m)

    # write_to_html(collected_matches, clean_text1, clean_text2, f1name, f2name)

    print()
