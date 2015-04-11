#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix

import WFMapping
from DepTree import DepTree
import dataTool

'''
This codes implements the OneLayerDepModel for stance classification.
DepTree.py, WFDict.py and Word->frequency mapping are required.
Author: Wei-Ming Chen
Date: 2015/03/08
Last Updated: 2015/03/08
'''

class OneLayerDepModel():
    # parsedLabelNews: The list of parsed label-news
    # if allowedSeedWordType = '[t][w]':
    #   allowedSeedWord[T][P]: a set of allowed words with `P` POS-Tag in topic T 
    # elif allowedSeedWordType = 'word':
    #   allowedSeedWord[T]: a set of allowed words (without considering POS tag)
    # elif allowedSeedWordType = 'tag':
    #   allowedSeedWord[T]: a set of allowe POS tag (without considering word)
    # 
    # allowedFirstLayerWord is similar to allowedSeedWord
    # allowedRel[T][P]
    def __init__(self, parsedLabelNews, allowedSeedWord, allowedSeedWordType, 
            allowedFirstLayerWord, allowedFirstLayerWordType, allowedRel):
        self.pln = parsedLabelNews
        self.asw = allowedSeedWord
        self.aswType = allowedSeedWordType
        self.aflw = allowedFirstLayerWord
        self.aflwType = allowedFirstLayerWordType
        self.ar = allowedRel
        self.seedVolc = dict() # seed word volcabulary
        self.__initSeedVolc()  
        self.newVolc = dict() # word volcabulary for first layer
        
    # TODO: word/word-tag/word-relation??
    # initialize the seed word volcabulary
    def __initSeedVolc(self):
        for topicId, seedWord in self.asw.items():
            for tag, wordSet in seedWord.items():
                addWordSetToVolc(wordSet, self.seedVolc)
        print('#seedVolc:', len(self.seedVolc), file=sys.stderr)

    def getDepTree(self, tdList, topicId):
        return DepTree(tdList)

    # generate X, y 
    def genXY(self):
        corpusEdgeList = list()
        for labelNews in self.pln:
            topicId = labelNews['statement_id'] # FIXME
            contentDep = labelNews['news']['content_dep'] #TODO: title, content, statement
            newsEdgeList = list()
            for depList in contentDep:
                # generate dependency graph for each dependency list
                dg = self.getDepTree(depList['tdList'], topicId)
                dg.setAllowedDepWord(self.aflw[topicId], type=self.aflwType)
                dg.setAllowedGovWord(self.aflw[topicId], type=self.aflwType)
                dg.setAllowedRel(self.ar[topicId])
                dg.setNowWord(self.asw[topicId], self.aswType)
                
                # go one step for searching dependencies (edges) which matches the rule
                edgeList = dg.searchOneStep()
                
                # add new word to volcabulary
                newWordSet = set([eW for rel,sP,sW,sT,eP,eW,eT in edgeList])
                addWordSetToVolc(newWordSet, self.newVolc)

                # save all the searched depenencies for later usage
                newsEdgeList.append(edgeList)

            # corpusEdgeList[newsIndex][depGraphIndex][edgeIndex]
            corpusEdgeList.append(newsEdgeList)

        print("#newVolc:", len(self.newVolc))

        # converting all extraced dependencies to features X
        # Here the features are the word counts from each seed word, 
        # so the dimension of X will be len(seedVolc) * len(newVolc)
        base = len(self.newVolc)
        XFeature = [defaultdict(int) for i in range(0, len(parsedLabelNews))]
        for i, newsEdgeList in enumerate(corpusEdgeList):
            for edgeList in newsEdgeList:
                for rel,sP,sW,sT,eP,eW,eT in edgeList:
                    index = self.seedVolc[sW] * base + self.newVolc[eW]
                    XFeature[i][index] += 1
        
        rows = list()
        cols = list()
        entries = list()
        for rowId, cntDict in enumerate(XFeature):
            for colId, cnt in cntDict.items():
                rows.append(rowId)
                cols.append(colId)
                entries.append(cnt)
        numRow = len(XFeature)
        numCol = len(self.seedVolc) * len(self.newVolc)
        X = csr_matrix((entries, (rows, cols)), shape=(numRow, 
            numCol), dtype=np.float64)
        y = np.array(getLabels(parsedLabelNews))

        return (X, y)


# get labels from the list of label-news
def getLabels(labelNewsList):
    mapping = { "neutral" : 1, "oppose": 0, "agree" : 2 } 
    labelList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in mapping:
            labelList.append(mapping[labelNews['label']])
    return labelList


# add a set of word to volcabulary
def addWordSetToVolc(wordSet, volc):
    for w in wordSet:
        if w not in volc:
            volc[w] = len(volc)


# TODO: calculate frequency from dependencies
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'parsedLabelNewsJson wordFrequencyMappingJson', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1]
    wordFrequencyMappingJsonFile = sys.argv[2]

    # load label-news
    with open(parsedLabelNewsJsonFile, 'r') as f:
        parsedLabelNews = json.load(f)
    parsedLabelNews = dataTool.data_cleaning(parsedLabelNews)

    WFDict = WFMapping.loadWFDict(wordFrequencyMappingJsonFile)

    # get the set of all possible topic
    topicSet = set()
    for labelNews in parsedLabelNews:
        topicSet.add(labelNews['statement_id'])

    # model setting
    seedWordPOSType = ['NN', 'NR'] 
    firstLayerPOSType = ['VA', 'VV', 'JJ', 'AD']
    thresList = [0.01, 0.005, 0.001, 0.0005, 0.00001]

    '''
    # all news are mixed to train and test
    for threshold in thresList:
        allowedSeedWord = dict() 
        allowedFirstLayerWord = dict()
        allowedRel = dict()
        for topicId in topicSet:
            allowedSeedWord[topicId] = WFMapping.getAllowedWords(WFDict[topicId], seedWordPOSType, threshold)
            allowedFirstLayerWord[topicId] = WFMapping.getAllowedWords(WFDict[topicId], firstLayerPOSType, threshold)
            allowedRel[topicId] = None
            
            for pos in seedWordPOSType:
                print('#%s:%d' % (pos, len(allowedSeedWord[topicId][pos])), end='\t')
            for pos in firstLayerPOSType:    
                print('#%s:%d' % (pos, len(allowedFirstLayerWord[topicId][pos])), end='\t')
            print('')

        # building the model
        oldm = OneLayerDepModel(parsedLabelNews, allowedSeedWord, 
            allowedFirstLayerWord, allowedRel)
        (X, y) = oldm.genXY()
    
        MLProcedure.runExperiments(X, y, clfList=['NaiveBayes', 'SVM'], 
            prefix='Threshold=%f' % (threshold))
    '''
    # news are divided into different topic to train and test
    labelNewsInTopic = dataTool.divideLabel(parsedLabelNews)
    for topicId, labelNewsList in labelNewsInTopic.items():
        for threshold in thresList:
            allowedSeedWord = dict() 
            allowedFirstLayerWord = dict()
            allowedRel = dict()
            allowedSeedWord[topicId] = WFMapping.getAllowedWords(WFDict[topicId], seedWordPOSType, threshold)
            allowedFirstLayerWord[topicId] = WFMapping.getAllowedWords(WFDict[topicId], firstLayerPOSType, threshold)
            allowedRel[topicId] = None
                
            for pos in seedWordPOSType:
                print('#%s:%d' % (pos, len(allowedSeedWord[topicId][pos])), end='\t')
            for pos in firstLayerPOSType:    
                print('#%s:%d' % (pos, len(allowedFirstLayerWord[topicId][pos])), end='\t')
            print('')

            # building the model
            oldm = OneLayerDepModel(labelNewsList, allowedSeedWord, 
                allowedFirstLayerWord, allowedRel)
            (X, y) = oldm.genXY()
        
            MLProcedure.runExperiments(X, y, clfList=['NaiveBayes', 'MaxEnt',  'SVM'], 
                prefix='topicId=%d, Threshold=%f' % (topicId,threshold))

    
