#!/usr/bin/env python3

import sys
import json
import math
import random
from collections import defaultdict

from sentiDictSum import readSentiDict
from dataPreprocess import divideLabel

# This module is for converting data to HCRF data format
# Last Updated: 2015/3/23

outputFolder = './HCRF/data'

def toHCRF(labelNewsList, sentiDict, trainXFile, testXFile, 
        trainLabelFile, testLabelFile, corpusFile, dictFile, 
        testSize=0.2, randomState=1, sentSep = ',', 
        wordSep = ' ', topicAware=False):

    # build dictionary
    volc = dict()
    for labelNews in labelNewsList:
        content = labelNews['news']['content_seg']
        for sent in content.split(sentSep):
            for w in sent.split(wordSep):
                if w not in volc:
                    volc[w] = len(volc)
    volcSize = len(volc)
    for w in sentiDict.keys():
        if w not in volc:
            volc[w]  = len(volc)
    
    # write corpus file
    (newsList, newsIdMap) = getNewsCorpus(labelNewsList)
    with open(corpusFile, 'w') as f:
        print(len(newsList), volcSize, sep=' ', file=f)
        for news in newsList:
            content = news['content_seg']
            for i, sent in enumerate(content.split(sentSep)):
                if i != 0:
                    print(',' ,end='', file=f)
                for j, w in enumerate(sent.split(wordSep)):
                    if j == 0:
                        print(volc[w], end='',file=f)
                    else:
                        print(' %d' % volc[w], end='',file=f)
            print('', file=f)
    
    # write sentiment dictionary file
    with open(dictFile, 'w') as f:
        for w, v in sentiDict.items():
            print(volc[w], v, sep=' ', file=f)

    # split training and testing file
    (trainLabelNewsList, testLabelNewsList) = splitData(
            labelNewsList, testSize, randomState, topicAware)
 
    # write train and test file
    writeXandLabel(trainLabelNewsList, trainXFile, 
            trainLabelFile, newsIdMap, sentSep)
    writeXandLabel(testLabelNewsList, testXFile, 
            testLabelFile, newsIdMap, sentSep)

    # for debugging
    with open(corpusFile + '.volc', 'w') as f:
        for k, v in sorted(list(volc.items()), key=lambda x:x[1]):
            print(k, v, file=f)
    with open(corpusFile + '.newsIdMap', 'w') as f:
        for k, v in sorted(list(newsIdMap.items()), key=lambda x:x[1]):
            print(k, v, file=f)

def getNewsCorpus(labelNewsList):
    newsList = list()
    newsIdMap = dict()
    for labelNews in labelNewsList:
        news_id = labelNews['news_id']
        news = labelNews['news']
        if news_id not in newsIdMap:
            newsIdMap[news_id] = len(newsIdMap)
            newsList.append(news)
    return (newsList, newsIdMap)

def splitData(labelNewsList, testSize, randomState, topicAware):
    if topicAware:
        pass #TODO
    else:
        # mapping text to integer
        m = { "agree": 0, "neutral": 1, "oppose": 2}
        y = [m[labelNews['label']] for labelNews in labelNewsList]
        # calculate expected number of each class (for train and test)
        num = defaultdict(int)
        for yi in y:
            num[yi] += 1
        total = len(labelNewsList)
        testNum = { k: math.ceil(v*testSize) for k, v in num.items() }
        trainNum = { k: num[k] - testNum[k] for k, v in num.items() }
        # random shuffle, and then split into train and test 
        index = [i for i in range(0, total)]
        random.seed(randomState);
        random.shuffle(index)
        
        nowNum = { k: 0 for k in num.keys() }
        trainIndex = list()
        testIndex = list()
        
        for i in index:
            if nowNum[y[i]] < trainNum[y[i]]:
                trainIndex.append(i)
                nowNum[y[i]] += 1
            else:
                testIndex.append(i)
        
        trainLabelNewsList = [labelNewsList[i] for i in trainIndex]
        testLabelNewsList = [labelNewsList[i] for i in testIndex]
        print("#train:", len(trainLabelNewsList))
        print("#test:", len(testLabelNewsList))
        return trainLabelNewsList, testLabelNewsList

def writeXandLabel(labelNewsList, xFile, labelFile, newsIdMap, sentSep):
    m = {"agree": 0, "neutral": 1, "oppose": 2}
    xFout = open(xFile, 'w')
    labelFout = open(labelFile, 'w')
    for labelNews in labelNewsList:
        sentNum = len(labelNews['news']['content_seg'].split(sentSep))
        #trainFile
        print('1,%d' % sentNum, file=xFout)
        for j in range(0, sentNum):
            if j != 0:
                print(',', end='', file=xFout)
            print(newsIdMap[labelNews['news_id']], end='', file=xFout)
        print('', file=xFout)
        #trainLabelFile
        print(m[labelNews['label']], file=labelFout)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'SegLabelNewsJsonFile SentiDictFile', file=sys.stderr)
        exit(-1)

    segLabelNewsJsonFile = sys.argv[1]
    sentiDictFile = sys.argv[2]

    with open(segLabelNewsJsonFile, 'r') as f:
        segLabelNews = json.load(f)

    sentiDict = readSentiDict(sentiDictFile)
    labelNewsPerTopic = divideLabel(segLabelNews)
    
    #topic divide data
    for topicId, labelNewsList in labelNewsPerTopic.items():
        prefix = '%s/zhtNewsTopic%d' % (outputFolder, topicId)
        toHCRF(labelNewsList, sentiDict, 
                trainXFile = prefix + '_dataTrain.csv',
                testXFile = prefix + '_dataTest.csv',
                trainLabelFile = prefix + '_seqLabelTrain.csv',
                testLabelFile = prefix + '_seqLabelTest.csv',
                corpusFile = prefix + '_corpus.txt',
                dictFile = prefix + '_sentiDict.txt', 
                testSize=0.2)
    



