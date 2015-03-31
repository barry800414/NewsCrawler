#!/usr/bin/env python3 

import sys
import json
import math
from operator import itemgetter

import dataPreprocess
from ChiSquareTable import ChiSquareTable

'''
This module is for feature selection (select word)
'''

ALL_POS = set()

def corpus2ChiSquareTable(labelNewsList, usingPOS=False, 
        w2i=None, i2w=None, sentSep=',', wordSep=' ', tagSep='/'):
    if w2i == None or i2w == None:
        w2i = dict()
        i2w = list()

    c2i = { "agree": 0, "neutral": 1, "oppose": 2 } 
    i2c = ["agree", "neutral", "oppose"]
    classDocCnt = [0, 0, 0] #classDocCnt[j]: number of doc with class j
    classWordCnt = list() #classWordCnt[i][j] number of doc with word i and class j
    
    for labelNews in labelNewsList:
        label = labelNews['label']
        classDocCnt[c2i[label]] += 1
        content = labelNews['news']['content_pos']
        docW = set()
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                # using word-tag as an item
                if usingPOS:
                    if (w, t) not in docW:
                        docW.add((w, t))
                        if (w, t) not in w2i:
                            w2i[(w,t)] = len(w2i)
                            i2w.append((w, t))
                            classWordCnt.append([0, 0, 0])
                        classWordCnt[w2i[(w,t)]][c2i[label]] += 1
                # using word as an item
                else:
                    if w not in docW:
                        docW.add(w)
                        if w not in w2i:
                            w2i[w] = len(w2i)
                            i2w.append(w)
                            classWordCnt.append([0, 0, 0])
                        classWordCnt[w2i[w]][c2i[label]] += 1
    table = ChiSquareTable.calcTable(len(c2i), len(w2i), classDocCnt, classWordCnt)
    return (table, w2i, i2w, c2i, i2c)

# return value: wPOSSet[wordId] is the set of POS tagger appeared in corpus
def getWordPOSSet(labelNewsList, w2i=None, i2w=None, sentSep=',', wordSep=' ', tagSep='/'):
    if w2i == None or i2w == None:
        w2i = dict()
        i2w = list()
    wPOSSet = [set() for i in range(0, len(i2w))]
    global ALL_POS
    for labelNews in labelNewsList:
        content = labelNews['news']['content_pos']
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if w not in w2i:
                    w2i[w] = len(w2i)
                    i2w.append(w)
                    wPOSSet.append(set())
                wPOSSet[w2i[w]].add(t)
                ALL_POS.add(t)
    return wPOSSet


# classMap[i]: the i-th class
# itemMap[i]: the i-th item
def printWord(chiTable, classMap, itemMap, allowedPOS, 
        wPOSSet, printValue=False, outfile=sys.stdout):
    # for each class
    for i, chiList in enumerate(chiTable):
        c = classMap[i]
        print('Class %s' % (c), end=':', file=outfile)
        
        # sort the list by chi square value
        sortedList = sorted(enumerate(chiList), key=itemgetter(1), reverse=True)
        for itemIndex, value in sortedList:
            if len(wPOSSet[itemIndex] & allowedPOS) == 0: #the word has no allowed tags
                continue
            print(' %s' % (itemMap[itemIndex]), end='', file=outfile)
            if printValue:
                print(';%.2f' % (value), end=' ', file=outfile)
        print('',file=outfile)

# classMap[i]: the i-th class
# itemMap[i]: the i-th item
def printWordTag(chiTable, classMap, itemMap, allowedPOS, 
        printValue=False, outfile=sys.stdout):
    # for each class
    for i, chiList in enumerate(chiTable):
        c = classMap[i]
        print('Class %s' % (c), end=':\n', file=outfile)
        
        # sort the list by chi square value
        sortedList = sorted(enumerate(chiList), key=itemgetter(1), reverse=True)
        for tag in allowedPOS:
            # filter word-tag with given tag
            print('\t%s:' % tag, end='', file=outfile)
            for itemIndex, value in sortedList:
                wt = itemMap[itemIndex]
                if wt[1] != tag:
                    continue
                print(' %s' % (itemMap[itemIndex][0]), end='', file=outfile)
                if printValue:
                    print(';%.2f' % (value), end=' ', file=outfile)
            print('',file=outfile)



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'tagLabelNewsJsonFile wordfSelectFile wordTagfSelectFile', file=sys.stderr)
        exit(-1)

    tagLabelNewsJsonFile = sys.argv[1]
    wordfSelectFile = sys.argv[2]
    wordTagfSelectFile = sys.argv[3]

    with open(tagLabelNewsJsonFile, 'r') as f:
        taggedLabelNewsList = json.load(f)
    
    labelNewsInTopic = dataPreprocess.divideLabel(taggedLabelNewsList)
    allowedPOS = set(['AD', 'JJ', 'NN', 'NR', 'VA', 'VV'])

    with open(wordfSelectFile, 'w') as f1, open(wordTagfSelectFile, 'w') as f2:
        for topicId, labelNewsList in labelNewsInTopic.items():
            # using word as item
            (wChiTable, w2i, i2w, c2i, i2c) = corpus2ChiSquareTable(labelNewsList)
            
            # using word & tag as item
            (wtChiTable, wt2i, i2wt, c2i, i2c) = corpus2ChiSquareTable(labelNewsList, usingPOS=True)
            
            # get all possible POS tagger of each word in corpus
            wPOSSet = getWordPOSSet(labelNewsList, w2i, i2w)
            
            # output for word feature selection file
            print('=====Topic:%d=====' % topicId, file=f1)
            printWord(wChiTable, i2c, i2w, allowedPOS, wPOSSet, outfile=f1)

            # output for word-tag feature selection file
            print('=====Topic:%d=====' % topicId, file=f2)
            printWordTag(wtChiTable, i2c, i2wt, allowedPOS, outfile=f2)
        
    #print('All POS tagger set', ALL_POS, file=sys.stderr)
