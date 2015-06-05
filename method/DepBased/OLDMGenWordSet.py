#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.grid_search import ParameterGrid

from DepTree import *
from PhraseDepTree import *
from RunExperiments import *
from Volc import *
from misc import *

'''
OLDM for generating word sets

Author: Wei-Ming Chen
Date: 2015/05/08
'''


class OneLayerDepModel():
    # depParsedLabelNews: The list of parsed label-news
    # if allowedSeedWordType = '[t][w]':
    #   allowedSeedWord[T][P]: a set of allowed words with `P` POS-Tag in topic T 
    # elif allowedSeedWordType = 'word':
    #   allowedSeedWord[T]: a set of allowed words (without considering POS tag)
    # elif allowedSeedWordType = 'tag':
    #   allowedSeedWord[T]: a set of allowe POS tag (without considering word)
    #
    # allowedFirstLayerWord is similar to allowedSeedWord
    #
    # volcDict: collection of dictionary
    def __init__(self, depParsedLabelNews, topicPhraseList=None):
        self.pln = depParsedLabelNews
        self.topicPhraseList = topicPhraseList
        self.init()
        
    def init(self):
        # the list to store the dependency trees of each doc
        # self.corpusDTList[i]: (topicId of doc i, the dep tree list of doc i)
        self.corpusDTList = list()
        for i, labelNews in enumerate(self.pln):
            topicId = labelNews['statement_id'] 
            contentDep = labelNews['news']['content_dep']
            newsDTList = list()
            for depList in contentDep:
                # generate dependency graph for each dependency list
                dg = self.getDepTree(depList['tdList'], topicId)
                if dg != None:
                    newsDTList.append(dg)
            self.corpusDTList.append((topicId, newsDTList))
            if (i+1) % 10 == 0:
                print('%cIntializing the model... Progress: (%d/%d)' % (13, i+1, len(self.pln)), end='', file=sys.stderr)
        print('', file=sys.stderr)
    
    # the pair volcabulary 
    def getVolcDict(self):
        return self.volcDict
    
    # generate dependency tree from typed dependencies
    def getDepTree(self, tdList, topicId):
        if self.topicPhraseList != None:
            pdt = PhraseDepTree(tdList, self.topicPhraseList[topicId])
            if pdt.isValid():
                pdt.construct()
                return pdt
            else:
                return None
        else:
            dt = DepTree(tdList)
            if dt.isValid():
                return dt
            else:
                return None

    # generate X, y. Must call setModel in advance 
    def genWordCnt(self, allowedSeedWord, allowedSeedWordType, allowedFirstLayerWord, 
            allowedFirstLayerWordType, allowedRel):
        self.asw = allowedSeedWord
        self.aswType = allowedSeedWordType
        self.aflw = allowedFirstLayerWord
        self.aflwType = allowedFirstLayerWordType
        self.ar = allowedRel

        # all retrieved edges in whole corpus
        corpusEdgeList = list()
        for topicId, newsDTList in self.corpusDTList:
            newsEdgeList = list()
            for dg in newsDTList:
                dg.reset()
                dg.setAllowedDepWord(self.aflw[topicId], type=self.aflwType)
                dg.setAllowedGovWord(self.aflw[topicId], type=self.aflwType)
                dg.setAllowedRel(self.ar[topicId])
                dg.setNowWord(self.asw[topicId], self.aswType)
                # go one step for searching dependencies (edges) which matches the rule
                edgeList = dg.searchOneStep(keepDirection=False)
                # save all the searched depenencies for later usage
                newsEdgeList.append(edgeList)

            # corpusEdgeList[newsIndex][depGraphIndex][edgeIndex]
            corpusEdgeList.append(newsEdgeList)

        # build the volcabulary for pair
        seedWordCnt = defaultdict(int)
        firstLayerWordCnt = defaultdict(int)
        for newsEdgeList in corpusEdgeList:
            self.extractPairs(newsEdgeList, seedWordCnt, firstLayerWordCnt)
        
        return (seedWordCnt, firstLayerWordCnt)

    def extractPairs(self, newsEdgeList, seedWordCnt, firstLayerWordCnt):
        for edgeList in newsEdgeList:
            for rel,sP,sW,sT,eP,eW,eT in edgeList:
                seedWordCnt[sW] += 1
                firstLayerWordCnt[eW] +=1 


# initialize allowed set. dictionary: word -> score
def initAllowedSet(topicSet, config, dictionary=None):
    if config['type'] == 'word': #using words in dictionary
        allowedSet = { topicId: set(dictionary.keys()) for topicId in topicSet }
    elif config['type'] == 'tag': #using tag
        allowedSet = { topicId: set(config['allow']) for topicId in topicSet }
    return allowedSet

def initOLDM(labelNewsList, topicPhraseList=None):
    oldm = OneLayerDepModel(labelNewsList, topicPhraseList)
    return oldm

def printWordCnt(wordCnt, filename):
    with open(filename, 'w') as f:
        sortedList = sorted(wordCnt.items(), key=lambda x:x[1], reverse=True)
        for word, cnt in sortedList:
            print(word, cnt, sep=':', file=f)


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage:', sys.argv[0], 'DepParsedLabelNewsJson ModelConfig SentiDictFile outFilePrefix', file=sys.stderr)
        exit(-1)

    depParsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    modelConfigFile = sys.argv[2]
    sentiDictFile = sys.argv[3]
    outFilePrefix = sys.argv[4]

    # load dependency parsed label news
    with open(depParsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)   
    # load model configs 
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)
    # sample document if neccessary
    labelNewsList = runSampleDoc(labelNewsList, config)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    # load phrase file
    topicPhraseList = loadPhraseFileFromConfig(config['phrase'])

    # model parameters #FIXME: allowed relation
    taskName = config['taskName']
    setting = config['setting']

    paramsIter = ParameterGrid(config['params'])

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)


    # intialize the model
    oldm = initOLDM(labelNewsList, topicPhraseList)
    toldm = { t: initOLDM(ln, topicPhraseList) for t, ln in labelNewsInTopic.items() }
 
    # ============= Run for self-train-test ===============
    print('For each topic ... ', file=sys.stderr)
    for t in topicSet:
        cnt = 0
        for p in paramsIter:
            allowedSeedWord = initAllowedSet(topicSet, p['seedWordType'])
            allowedFirstLayerWord = initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
            allowedRel = { t: None for t in topicSet }
            (seedWordCnt, firstLayerWordCnt) = toldm[t].genWordCnt(allowedSeedWord, 
                    p['seedWordType']['type'], allowedFirstLayerWord, 
                    p['firstLayerType']['type'], allowedRel)

            printWordCnt(seedWordCnt, outFilePrefix + '_T%d_sW.txt' % t)
            printWordCnt(firstLayerWordCnt, outFilePrefix + '_T%d_flW.txt' % t)
            cnt += 1
        assert cnt == 1
                
    # ============= Run for all-train-test & leave-one-test ================
    print('For all mixed ... ', file=sys.stderr)
    for p in paramsIter:
        allowedSeedWord = initAllowedSet(topicSet, p['seedWordType'])
        allowedFirstLayerWord = initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
        allowedRel = { t: None for t in topicSet }
        (seedWordCnt, firstLayerWordCnt) = oldm.genWordCnt(allowedSeedWord, 
                p['seedWordType']['type'], allowedFirstLayerWord, 
                p['firstLayerType']['type'], allowedRel)
        printWordCnt(seedWordCnt, outFilePrefix + '_TAll_sW.txt')
        printWordCnt(firstLayerWordCnt, outFilePrefix + '_TAll_flW.txt')
    
    
