#!/usr/bin/env python3 

import sys
import json
import math
from operator import itemgetter

import dataPreprocess

INF=9999999.0

def chiSquareTable(labelNewsList, w2i=None, i2w=None, sentSep=',', 
        wordSep=' ', tagSep='/'):
    if w2i == None or i2w == None:
        w2i = dict()
        i2w = list()

    c2i = { "agree": 0, "neutral": 1, "oppose": 2 } 
    i2c = ["agree", "neutral", "oppose"]
    classNum = [0, 0, 0] #classNum[j]: number of doc with class j
    wNum = list() #wNum[i][j] number of doc with word i and class j
    
    for labelNews in labelNewsList:
        label = labelNews['label']
        classNum[c2i[label]] += 1
        content = labelNews['news']['content_pos']
        docW = set()
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if w not in docW:
                    docW.add(w)
                    if w not in w2i:
                        w2i[w] = len(w2i)
                        i2w.append(w)
                        wNum.append([0, 0, 0])
                    wNum[w2i[w]][c2i[label]] += 1
    
    chiTable = [[0 for i in range(0, len(w2i))] for j in range(0, len(c2i))]
    for c in range(0, len(c2i)):
        for w in range(0, len(w2i)):
            chiTable[c][w] = chiSquare(w, c, classNum, wNum)

    return (chiTable, w2i, i2w, c2i, i2c)

# w: index of word, c: index of class
def chiSquare(w, c, classNum, wNum):
    A = wNum[w][c]
    B = classNum[c] - A
    C = sum(wNum[w]) - A
    D = (sum(classNum) - classNum[c]) - C
    N = A + B + C + D
    deno = ((A+C) * (B+D) * (A+B) * (C+D))
    if deno < 0:
        print(deno, file=sys.stderr)
        print(A, B, C, D, file=sys.stderr)
    if deno == 0:
        return INF
    else:
        value = (N * math.pow((A*D - C*B), 2.0)) / deno
        return value 

def printChiTable(chiTable, i2c, i2w, outfile=sys.stdout, printValue=False):
    for i, chiList in enumerate(chiTable):
        c = i2c[i]
        print('Class %s' % (c), end=':', file=outfile)
        sortedList = sorted(enumerate(chiList), key=itemgetter(1), reverse=True)
        for wIndex, value in sortedList:
            print(' %s' % (i2w[wIndex]), end='', file=outfile)
            if printValue:
                print(';%.2f' % (value), end=' ', file=outfile)
        print('',file=outfile)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'tagLabelNewsJsonFile', file=sys.stderr)
        exit(-1)

    tagLabelNewsJsonFile = sys.argv[1]

    with open(tagLabelNewsJsonFile, 'r') as f:
        taggedLabelNewsList = json.load(f)
    
    labelNewsInTopic = dataPreprocess.divideLabel(taggedLabelNewsList)

    for topicId, labelNewsList in labelNewsInTopic.items():
        (chiTable, w2i, i2w, c2i, i2c) = chiSquareTable(labelNewsList)
        print('=====Topic:%d=====' % topicId)
        printChiTable(chiTable, i2c, i2w)
    
        
