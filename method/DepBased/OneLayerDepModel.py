#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix

import WFMapping
from DepTree import DepTree
import dataTool
from Volc import Volc

'''
This codes implements the OneLayerDepModel for stance classification.
DepTree.py, WFDict.py and Word->frequency mapping are required.

Improved version of OneLayerDepModel
 1.remove < 1 dimension (DONE)
 2.word clustering  
 3.highest frequency?
 4.allowed word config

Author: Wei-Ming Chen
Date: 2015/05/08
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
    def __init__(self, parsedLabelNews):
        self.pln = parsedLabelNews
        self.init()
        
    def init(self):
        self.setModelFlag = False
        # the list to store the dependency trees of each doc
        # self.corpusDTList[i]: (topicId of doc i, the dep tree list of doc i)
        self.corpusDTList = list()
        for labelNews in self.pln:
            topicId = labelNews['statement_id'] # FIXME
            contentDep = labelNews['news']['content_dep'] #TODO: title, content, statement
            newsDGList = list()
            for depList in contentDep:
                # generate dependency graph for each dependency list
                dg = self.getDepTree(depList['tdList'], topicId)
                if dg != None:
                    newsDGList.append(dg)
            self.corpusDTList.append((topicId, newsDGList))

    def getVolc(self):
        return self.volc

    # generate dependency tree from typed dependencies
    def getDepTree(self, tdList, topicId):
        dt = DepTree(tdList)
        if dt.isValid():
            return dt
        else:
            return None

    def setModel(self, allowedSeedWord, allowedSeedWordType, 
            allowedFirstLayerWord, allowedFirstLayerWordType, 
            allowedRel, threshold=0, debugLevel=0, 
            debugFile=sys.stderr):
        self.asw = allowedSeedWord
        self.aswType = allowedSeedWordType
        self.aflw = allowedFirstLayerWord
        self.aflwType = allowedFirstLayerWordType
        self.ar = allowedRel
        self.threshold = threshold
        self.debugLevel = debugLevel
        self.debugFile = debugFile
        self.setModelFlag = True

    # generate X, y. Must call setModel in advance 
    def genXY(self):
        if self.setModelFlag == False:
            return 

        # all retrieved edges in whole corpus
        corpusEdgeList = list()
        for topicId, newsDGList in self.corpusDTList:
            newsEdgeList = list()
            for dg in newsDGList:
                dg.reset()
                dg.setAllowedDepWord(self.aflw[topicId], type=self.aflwType)
                dg.setAllowedGovWord(self.aflw[topicId], type=self.aflwType)
                dg.setAllowedRel(self.ar[topicId])
                dg.setNowWord(self.asw[topicId], self.aswType)
                # go one step for searching dependencies (edges) which matches the rule
                edgeList = dg.searchOneStep()
                
                # save all the searched depenencies for later usage
                newsEdgeList.append(edgeList)

            # corpusEdgeList[newsIndex][depGraphIndex][edgeIndex]
            corpusEdgeList.append(newsEdgeList)

        # build the dictionary
        volc = Volc()
        docF = defaultdict(int) # doc frequency for each pair
        for newsEdgeList in corpusEdgeList:
            docPairSet = set()
            for edgeList in newsEdgeList:
                for rel,sP,sW,sT,eP,eW,eT in edgeList:
                    if (sW, eW) not in volc:
                        volc.addWord((sW, eW))
                        #volc[(sW,eW)] = len(volc)
                    docPairSet.add(volc[(sW, eW)])
            for key in docPairSet:
                docF[key] += 1        

        # if the doc frequency of that pair is less than or equal 
        # to threshold, then discard it
        if self.threshold != None:
            docF = volc.shrinkVolcByDocF(docF, self.threshold)

        if self.debugLevel > 0:
            print('# distinct pairs: ', len(volc), file=sys.stderr)
            for (sW, eW), index in volc.items():
                print(sW, '/', eW, index, file=self.debugFile)

        # converting all extraced dependencies to features X
        # Here the features are the word counts from each seed word, 
        # first layer word pair
        XFeature = [defaultdict(int) for i in range(0, len(self.pln))]
        for i, newsEdgeList in enumerate(corpusEdgeList):
            for edgeList in newsEdgeList:
                for rel,sP,sW,sT,eP,eW,eT in edgeList:
                    if (sW, eW) in volc:
                        XFeature[i][volc[(sW, eW)]] += 1
        
        rows = list()
        cols = list()
        entries = list()
        for rowId, cntDict in enumerate(XFeature):
            for colId, cnt in cntDict.items():
                rows.append(rowId)
                cols.append(colId)
                entries.append(cnt)
        numRow = len(XFeature)
        numCol = len(volc)
        X = csr_matrix((entries, (rows, cols)), shape=(numRow, 
            numCol), dtype=np.float64)
        y = np.array(getLabels(self.pln))

        # update volc
        self.volc = volc
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
            volc.addWord(w)
            #volc[w] = len(volc)
        

# temporally deprecated
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

    
