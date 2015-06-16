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
            if (i+1) % 100 == 0:
                print('%cGenerating dependency trees ... Progress:(%d/%d)' % (13, i+1, len(self.pln)), end='', file=sys.stderr)
        print('', file=sys.stderr)
        self.corpusDTList = corpusDTList

    def getVolcDict(self):
        return self.volcDict

    # copy original volcabulary
    def setVolcDict(self, volcDict):
        if volcDict is None:
            self.volcDict = { 'main': Volc(), 'holder': None, 'opinion': None, 'target': None }
        else:
            self.volcDict = dict()
            self.volcDict['main'] = Volc()
            for type in ['holder', 'opinion', 'target']:
                if type in volcDict and volcDict[type] is not None:
                    self.volcDict[type] = volcDict[type].copy()
                else:
                    self.volcDict[type] = None

    # keyTypeList: The list of key types to be used as opinion key ('HOT', 'HT', 'OT', 'HO', 'T', 'H')
    # opnNameList: The list of selected opinion name 
    # sentiDict: sentiment dictionary
    # negSepList: the list of boolean flag to indicate whether negation pattern is represented separated
    def genXY(self, pTreeList, negPList, sentiDict, volcDict, 
            keyTypeList, opnNameList, negSepList, minCnt):
        self.pTL = pTreeList
        self.nPL = negPList
        self.kTL = keyTypeList
        self.opnNL = opnNameList
        self.sD = sentiDict
        self.nSL = negSepList
        self.minCnt = minCnt 
        self.setVolcDict(volcDict)
        
        print('Extracting Opinions(tree pattern matching) ...', end='',file=sys.stderr)
        opnCntList = list() # the list to save all opinions in each document
        docOpnCnt = defaultdict(int) # opnKey -> document frequency
        for i, newsDTList in enumerate(self.corpusDTList):
            opnDict = self.extractOpn(newsDTList)
            opnCnt = self.countOpn(opnDict)
            for key in opnCnt.keys():
                docOpnCnt[self.volcDict['main'][key]] += 1
            opnCntList.append(opnCnt)

            if (i+1) % 100 == 0:
                print('%cExtracting Opinions(tree pattern matching) ... Progress(%d/%d)' % (13, i+1, 
                    len(self.corpusDTList)), end='', file=sys.stderr) 
        print('', file=sys.stderr)

        # reduce volcabulary size
        self.volcDict['main'].shrinkVolcByDocF(docOpnCnt, self.minCnt)

        # convert to X, y
        rows = list()
        cols = list()
        entries = list()
        for rowId, opnCnt in enumerate(opnCntList):
            for opnKey, value in opnCnt.items():
                if opnKey not in self.volcDict['main']:
                    continue
                colId = self.volcDict['main'][opnKey]
                rows.append(rowId)
                cols.append(colId)
                entries.append(value)
        numRow = len(opnCntList)
        numCol = len(self.volcDict['main'])
        X = csr_matrix((entries, (rows, cols)), shape=(numRow, 
            numCol), dtype=np.float64)
        y = np.array(getLabels(self.pln))
        
        return (X, y)

    # opnDict: a dictionary (opinion-type-name -> list of opinions)
    # return: a dictionary (opnKey -> count) 
    def countOpn(self, opnDict):
        opnCnt = defaultdict(int)
        for opnName, opns in opnDict.items():
            # ignore the opinions which are not selected
            if self.opnNL != None and opnName not in self.opnNL:
                continue
            for opn in opns:
                for keyType in self.kTL:
                    for negSep in self.nSL:
                        keyValue = OpinionModel.getOpnKeyValue(opn, keyType, self.sD, negSep)
                        if keyValue != None:
                            (key, value) = keyValue
                            opnCnt[key] += value
                            self.volcDict['main'].addWord(key)
                        
        return opnCnt
        

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
                    results[i] = Opinion.genOpnFromDict(results[i], self.volcDict)

                opnDict[pTree.name].extend(results)
        return opnDict

    # get key of opinion object
    def getOpnKeyValue(opn, keyType, sentiDict=None, negSep=False):
        if keyType == 'HT' or keyType == 'T' or keyType == 'H':
            assert sentiDict != None
        
        if keyType == 'HOT':
            return opn.getKeyHOT(negSep)
        elif keyType == 'HT':
            return opn.getKeyHT(sentiDict, negSep)
        elif keyType == 'H':
            return opn.getKeyH(sentiDict, negSep)
        elif keyType == 'HO':
            return opn.getKeyHO(negSep)
        elif keyType == 'OT':
            return opn.getKeyOT(negSep)
        elif keyType == 'T':
            return opn.getKeyT(sentiDict, negSep)

    def printOpnCnt(opnCnts, outfile=sys.stdout):
        for opnName, opnCnt in opnCnts.items():
            print(opnName, file=outfile)
            for key, cnt in sorted(opnCnt.items(), key = lambda x:x[1], reverse=True):
                print(key, cnt, sep=',', file=outfile)


def initOM(labelNewsList, topicPhraseList=None):
    om = OpinionModel(labelNewsList, topicPhraseList)
    return om

# generate opinion model features
def genXY(om, params, preprocess, minCnt, pTreeList, negPList=None, sentiDict=None, volcDict=None):
    print('generating opinion model features ...', file=sys.stderr)
    p = params
    (X, y) = om.genXY(pTreeList, negPList, sentiDict, volcDict, 
                p['keyTypeList'], p['opnNameList'], p['negSepList'], 
                minCnt)
    if preprocess != None:
        X = DataTool.preprocessX(X, preprocess['method'], preprocess['params'])
    volcDict = om.getVolcDict()
    assert X.shape[1] == len(volcDict['main'])
    return (X, y, volcDict)

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('Usage:', sys.argv[0], 'DepParsedLabelNews ModelConfigFile TreePatternFile NegPatternFile SentiDictFile', file=sys.stderr)
        exit(-1)

    depParsedLabelNewsJsonFile = sys.argv[1]
    modelConfigFile = sys.argv[2]
    patternFile = sys.argv[3]
    negPatternFile = sys.argv[4]
    sentiDictFile = sys.argv[5]
    if len(sys.argv) == 7:
        topicTargetFile = sys.argv[6]
        #TODO

    # load model config
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)
    # load label news
    with open(depParsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    # sample document if neccessary
    labelNewsList = runSampleDoc(labelNewsList, config)
    
    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)
    newsIdList = { t:[ln['news_id'] for ln in labelNewsInTopic[t]] for t in topicSet }
    newsIdList['All'] = [ln['news_id'] for ln in labelNewsList] 

    # load pattern trees 
    pTreeList = TP.loadPatterns(patternFile)
    # load negation pattern file
    negPList = NP.loadNegPatterns(negPatternFile)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    # load volcabulary file
    topicVolcDict = loadVolcFileFromConfig(config['volc'], topicSet)
    # load phrase file
    topicPhraseList = loadPhraseFileFromConfig(config['phrase'])

    # model parameters 
    toRun = config['toRun']
    taskName = config['taskName']
    preprocess = config['preprocess']
    minCnt = config['minCnt']
    setting = config['setting']
    targetScore = config['setting']['targetScore'] 
    
    paramsIter = ParameterGrid(config['params'])

    ResultPrinter.printFirstLine()

    # intialize the model
    print('Intializing the model...', file=sys.stderr)
    if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
        om = initOM(labelNewsList, topicPhraseList)
    
    if 'SelfTrainTest' in toRun:
        tom = { t: initOM(ln, topicPhraseList) for t, ln in labelNewsInTopic.items() }
 
    # ============= Run for self-train-test ===============
    if 'SelfTrainTest' in toRun:
        print('Self-Train-Test...', file=sys.stderr)
        for t in topicSet:
            #if t != 2:
            #    continue
            for p in paramsIter:
                (X, y, newVolcDict) = genXY(tom[t], p, preprocess, minCnt, pTreeList,
                    negPList, sentiDict, topicVolcDict[t])
                expLog = RunExp.runTask(X, y, newVolcDict, newsIdList[t], 'SelfTrainTest', p, topicId=t, **setting)
            with open('%s_SelfTrainTest_topic%d.pickle' % (taskName, t), 'w+b') as f:
                pickle.dump(expLog, f)
    
    # ============= Run for all-train-test & leave-one-test ================
    print('All-Train-Test & Leave-One-Test ...', file=sys.stderr)
    for p in paramsIter:
        if 'AllTrainTest' in toRun:
            (X, y, newVolcDict) = genXY(om, p, preprocess, minCnt, pTreeList, 
                    negPList, sentiDict, topicVolcDict['All'])
            expLog = RunExp.runTask(X, y, newVolcDict, newsIdList['All'], 'AllTrainTest', p, topicMap=topicMap, **setting)
            with open('%s_AllTrainTest.pickle' %(taskName), 'w+b') as f:
                pickle.dump(expLog, f)
        if 'LeaveOneTest' in toRun:
            for t in topicSet:
                expLog = RunExp.runTask(X, y, newVolcDict, newsIdList['All'], 'LeaveOneTest', p, topicMap=topicMap, topicId=t, **setting)
                with open('%s_LeaveOneTest_topic%d.pickle' %(taskName, t), 'w+b') as f:
                    pickle.dump(expLog, f)

