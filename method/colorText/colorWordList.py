#!/usr/bin/env python3 
import sys
import json
from sentiDictSum import readSentiDict
from colorText import *

'''
for coloring the frequent word list by sentiment dictionary
word list is a file with word-frequency pairs
each line is a pair of word-frequency 
'''

def loadWfList(filename):
    wfList = list()
    with open(filename, 'r') as f:
        for line in f:
            entry = line.strip().split('\t')
            assert len(entry) == 2
            wfList.append((entry[0], int(entry[1])))
    return wfList

def writeWfList(filename, wfList):
    with open(filename, 'w') as fout:
        for w, f in wfList:
            print('%s\t%d' % (w, f), file=fout)

def coloringWfList(wfList, wordColorForSent):
    colorWfList = list()
    for w, f in wfList:
        if w in wordColorForSent:
            colorW = ct2(w, wordColorForSent[w])
        else:
            colorW = w
        colorWfList.append((colorW,f))
    return colorWfList

if __name__ == '__main__':
    if len(sys.argv)!= 4:
        print('Usage:', sys.argv[0], 'wordFrequencyList sentiDict coloredWordList', file=sys.stderr)
        exit(-1)
    
    wfListFile = sys.argv[1]
    sentiDictFile = sys.argv[2]
    outWfListFile = sys.argv[3]

    # load sentiment lexicon & 
    # generate word -> color mapping (for sentiment lexicon)
    sentiDict = readSentiDict(sentiDictFile)
    wordColorForSent = dictToWordColorMapping(sentiDict)

    # load word-frequency list
    wfList = loadWfList(wfListFile)

    # coloring word-frequency list
    colorWfList = coloringWfList(wfList, wordColorForSent)
    
    # write word-frequency list
    writeWfList(outWfListFile, colorWfList)


