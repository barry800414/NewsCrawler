#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.grid_search import ParameterGrid

import TreePattern as TP
import DepTree as DT
from PhraseDepTree import *
import NegPattern as NP
from Volc import *
from Opinion import *
from RunExperiments import *
from misc import *

class OpinionModel:
    def __init__(self, depParsedLabelNews, topicPhraseList=None):
        self.setModelFlag = False
        self.pln = depParsedLabelNews
        self.tPL = topicPhraseList
        self.init()

    # generate (phrase) dependency trees
    def init(self):
        print('Generating dependency trees ... ', end='',file=sys.stderr)
        corpusDTList = list()
        for i, ln in enumerate(self.pln):
            newsDTList = list()
            topicId = ln['statement_id']
            contentDep = ln['news']['content_dep']
            # for each dependency tree
            for depObj in contentDep:
                tdList = depObj['tdList']
                if self.tPL != None:
                    depTree = PDT.PhraseDepTree(tdList, self.tPL[topicId])
                else:
                    depTree = DT.DepTree(tdList)
                newsDTList.append(depTree)
            corpusDTList.append(newsDTList)
            if (i+1) % 10 == 0:
                print('%cGenerating dependency trees ... Progress:(%d/%d)' % (13, i+1, len(self.pln)), end='', file=sys.stderr)
        print('', file=sys.stderr)
        self.corpusDTList = corpusDTList

    # keyTypeList: The list of key types to be used as opinion key ('HOT', 'HT', 'OT', 'HO', 'T', 'H')
    # opnNameList: The list of selected opinion name 
    # sentiDict: sentiment dictionary
    # negSepList: the list of boolean flag to indicate whether negation pattern is represented separated
    def genWordCnt(self, pTreeList, negPList, sentiDict, keyTypeList, opnNameList, negSepList):
        self.pTL = pTreeList
        self.nPL = negPList
        self.kTL = keyTypeList
        self.opnNL = opnNameList
        self.sD = sentiDict
        self.nSL = negSepList
        
        print('Extracting Opinions(tree pattern matching) ...', end='',file=sys.stderr)
        hdWordCnt = defaultdict(int)
        opnWordCnt = defaultdict(int)
        tgWordCnt = defaultdict(int)
        for i, newsDTList in enumerate(self.corpusDTList):
            opnDict = self.extractOpn(newsDTList)
            self.countOpn(opnDict, hdWordCnt, opnWordCnt, tgWordCnt)

            if (i+1) % 10 == 0:
                print('%cExtracting Opinions(tree pattern matching) ... Progress(%d/%d)' % (13, i+1, 
                    len(self.corpusDTList)), end='', file=sys.stderr) 
        print('', file=sys.stderr)
        return (hdWordCnt, opnWordCnt, tgWordCnt)

    # opnDict: a dictionary (opinion-type-name -> list of opinions)
    # return: a dictionary (opnKey -> count) 
    def countOpn(self, opnDict, hdWordCnt, opnWordCnt, tgWordCnt):
        for opnName, opns in opnDict.items():
            # ignore the opinions which are not selected
            if self.opnNL != None and opnName not in self.opnNL:
                continue
            for opn in opns:
                if opn.hdW is not None:
                    hdWordCnt[opn.hdW] += 1
                if opn.opnW is not None:
                    opnWordCnt[opn.opnW] += 1
                if opn.tgW is not None:
                    tgWordCnt[opn.tgW] += 1
            

    # depParsedNews: dependency parsed news 
    # return: a dictionary (opinion-type-name -> list of opinions)
    def extractOpn(self, newsDTList):
        opnDict = dict()
        
        # for each dependency tree
        for depTree in newsDTList:
            # for each pattern tree
            for pTree in self.pTL:
                if pTree.name not in opnDict:
                    opnDict[pTree.name] = list()
                results = pTree.match(depTree) # a list of opinions (dict)
                
                # find negation pattern
                if self.nPL != None:
                    for r in results:
                        negCntDict = NP.checkAllNegPattern(self.nPL,
                                depTree, pTree, r['mapping'])
                        if len(negCntDict) > 0:
                            r['neg'] = negCntDict
                        del r['mapping']
                
                # convert to Opinion objects
                for i in range(0, len(results)):
                    results[i] = Opinion.genOpnFromDict(results[i], None)

                opnDict[pTree.name].extend(results)
        return opnDict

def initOM(labelNewsList, topicPhraseList=None):
    om = OpinionModel(labelNewsList, topicPhraseList)
    return om

if __name__ == '__main__':
    if len(sys.argv) != 7:
        print('Usage:', sys.argv[0], 'DepParsedLabelNews ModelConfigFile TreePatternFile NegPatternFile SentiDictFile outFilePrefix', file=sys.stderr)
        exit(-1)

    depParsedLabelNewsJsonFile = sys.argv[1]
    modelConfigFile = sys.argv[2]
    patternFile = sys.argv[3]
    negPatternFile = sys.argv[4]
    sentiDictFile = sys.argv[5]
    outFilePrefix = sys.argv[6]
    
    # load model config
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)
    # load label news
    with open(depParsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    # sample document if neccessary
    labelNewsList = runSampleDoc(labelNewsList, config)
        
    # load pattern trees 
    pTreeList = TP.loadPatterns(patternFile)
    # load negation pattern file
    negPList = NP.loadNegPatterns(negPatternFile)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    # load phrase file
    topicPhraseList = loadPhraseFileFromConfig(config['phrase'])

    # model parameters 
    setting = config['setting']
    
    paramsIter = ParameterGrid(config['params'])

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)


    # intialize the model
    print('Intializing the model...', file=sys.stderr)
    om = initOM(labelNewsList, topicPhraseList)
    tom = { t: initOM(ln, topicPhraseList) for t, ln in labelNewsInTopic.items() }
 
    # ============= Run for self-train-test ===============
    print('For each topic ... ', file=sys.stderr)
    for t in topicSet:
        cnt = 0
        for p in paramsIter:
            (hdWordCnt, opnWordCnt, tgWordCnt) = tom[t].genWordCnt(pTreeList, negPList, sentiDict,
                p['keyTypeList'], p['opnNameList'], p['negSepList'])
            printWordCnt(hdWordCnt, outFilePrefix + '_T%d_hdW.txt' % t)
            printWordCnt(opnWordCnt, outFilePrefix + '_T%d_opnW.txt' % t)
            printWordCnt(tgWordCnt, outFilePrefix + '_T%d_tgW.txt' % t)
            cnt += 1
        assert cnt == 1
    
    # ============= Run for all-train-test & leave-one-test ================
    print('For all mixed ... ', file=sys.stderr)
    for p in paramsIter:
        (hdWordCnt, opnWordCnt, tgWordCnt) = om.genWordCnt(pTreeList, negPList, sentiDict,
                p['keyTypeList'], p['opnNameList'], p['negSepList'])
        printWordCnt(hdWordCnt, outFilePrefix + '_TAll_hdW.txt')
        printWordCnt(opnWordCnt, outFilePrefix + '_TAll_opnW.txt')
        printWordCnt(tgWordCnt, outFilePrefix + '_TAll_tgW.txt')

