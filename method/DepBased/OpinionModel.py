#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.grid_search import ParameterGrid

import TreePattern as TP
import DepTree as DT
import PhraseDepTree as PDT
import NegPattern as NP
from Volc import Volc
from Opinion import *
from sentiDictSum import readSentiDict
from RunExperiments import *
from misc import *

#TODO: init 
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

    def getVolc(self):
        return self.volc

    # keyTypeList: The list of key types to be used as opinion key ('HOT', 'HT', 'OT', 'HO', 'T', 'H')
    # opnNameList: The list of selected opinion name 
    # sentiDict: sentiment dictionary
    # negSepList: the list of boolean flag to indicate whether negation pattern is represented separated
    def genXY(self, pTreeList, negPList=None, sentiDict=None, wVolc=None, 
            keyTypeList=['HOT'], opnNameList=None, negSepList=[False], minCnt=2):
        self.pTL = pTreeList
        self.nPL = negPList
        self.wVolc = wVolc # word vocabulary
        self.kTL = keyTypeList
        self.opnNL = opnNameList
        self.sD = sentiDict
        self.nSL = negSepList
        self.minCnt = minCnt 
        
        volc = Volc()
        
        print('Extracting Opinions(tree pattern matching) ...', end='',file=sys.stderr)
        opnCntList = list() # the list to save all opinions in each document
        docOpnCnt = defaultdict(int) # opnKey -> document frequency
        for i, newsDTList in enumerate(self.corpusDTList):
            opnDict = self.extractOpn(newsDTList, wVolc)
            opnCnt = self.countOpn(opnDict, volc)
            for key in opnCnt.keys():
                docOpnCnt[volc[key]] += 1
            opnCntList.append(opnCnt)

            if (i+1) % 10 == 0:
                print('%cExtracting Opinions(tree pattern matching) ... Progress(%d/%d)' % (13, i+1, 
                    len(self.corpusDTList)), end='', file=sys.stderr) 
        print('', file=sys.stderr)

        # reduce volcabulary size
        volc.shrinkVolcByDocF(docOpnCnt, self.minCnt)

        # convert to X, y
        rows = list()
        cols = list()
        entries = list()
        for rowId, opnCnt in enumerate(opnCntList):
            for opnKey, value in opnCnt.items():
                if opnKey not in volc:
                    continue
                colId = volc[opnKey]
                rows.append(rowId)
                cols.append(colId)
                entries.append(value)
        numRow = len(opnCntList)
        numCol = len(volc)
        X = csr_matrix((entries, (rows, cols)), shape=(numRow, 
            numCol), dtype=np.float64)
        y = np.array(getLabels(self.pln))
        
        # update volcabulary
        self.volc = volc
        
        return (X, y)

    # opnDict: a dictionary (opinion-type-name -> list of opinions)
    # volc: vocabulary for opinion (key)
    # return: a dictionary (opnKey -> count) 
    def countOpn(self, opnDict, volc):
        opnCnt = defaultdict(int)
        for opnName, opns in opnDict.items():
            # ignore the opinions which are not selected
            if self.opnNL != None and opnName not in self.opnNL:
                continue
            for opn in opns:
                for keyType in self.kTL:
                    for negSep in self.nSL:
                        (key, value) = OpinionModel.getOpnKeyValue(opn, keyType, sentiDict, negSep)
                        opnCnt[key] += value
                        volc.addWord(key)
                        
        return opnCnt
        

    # depParsedNews: dependency parsed news 
    # wVolc: word vocabulary
    # return: a dictionary (opinion-type-name -> list of opinions)
    def extractOpn(self, newsDTList, wVolc=None):
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
                    results[i] = Opinion.genOpnFromDict(results[i], wVolc)

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


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('Usage:', sys.argv[0], 'DepParsedLabelNews ModelConfigFile TreePatternFile NegPatternFile SentiDictFile [-p PhraseFile] [-v VolcFile]', file=sys.stderr)
        exit(-1)

    depParsedLabelNewsJsonFile = sys.argv[1]
    modelConfigFile = sys.argv[2]
    patternFile = sys.argv[3]
    negPatternFile = sys.argv[4]
    sentiDictFile = sys.argv[5]
    
    # load model config
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)
    # load label news
    with open(depParsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    # load pattern trees 
    pTreeList = TP.loadPatterns(patternFile)
    # load negation pattern file
    negPList = NP.loadNegPatterns(negPatternFile)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    # load other files
    topicPhraseList = None
    wVolc = None
    wVolcPrefix = ''
    for i in range(6, len(sys.argv)):
        if sys.argv[i] == '-p' and len(sys.argv) > i:
            # load phrase file
            phrasesJsonFile = sys.argv[i+1]
            topicPhraseList = loadPhraseFile(phrasesJsonFile)
            i = i + 1
        elif sys.argv[i] == '-v' and len(sys.argv) > i:
            # load word volcabulary file
            wordVolcFile = sys.argv[i+1]
            wVolcPrefix = getFileNamePrefix(wordVolcFile)
            wVolc = Volc()
            wVolc.load(wordVolcFile)
    
    # model parameters #FIXME: allowed relation
    randSeedList = config['setting']['randSeedList']
    paramsIter = ParameterGrid(config['params'])
    clfList = config['setting']['clfList']
    modelName = config['setting']['modelName']
    dataset = config['setting']['dataset']

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabel(labelNewsList)

    ResultPrinter.printFirstLine()

    # intialize the model
    print('Intializing the model...', file=sys.stderr)
    #om = OpinionModel(labelNewsList, topicPhraseList)
    tom = dict()
    for topicId, labelNewsList in labelNewsInTopic.items():
        #if topicId == 2:
        tom[topicId] = OpinionModel(labelNewsList, topicPhraseList) 
 
    # ============= Run for self-train-test ===============
    print('Self-Train-Test...', file=sys.stderr)
    for t in topicSet:
        #if t != 2:
        #    continue
        bestR = None
        for p in paramsIter:
            (X, y) = tom[t].genXY(pTreeList, negPList, sentiDict, wVolc, 
                p['keyTypeList'], p['opnNameList'], p['negSepList'], 
                p['minCnt'])
            volc = tom[t].getVolc()
            rsList = RunExp.runTask(X, y, volc, 'SelfTrainTest', 
                    p, clfList, topicId=t, randSeedList=randSeedList)
            bestR = keepBestResult(bestR, rsList, 'MacroF1')
        with open('%s_%s_%s_SelfTrainTest_topic%d.pickle' % (modelName, 
            dataset, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)

    
    # ============= Run for all-train-test ================
    print('All-Train-Test...', file=sys.stderr)
    bestR = None
    for p in paramsIter:
        (X, y) = om.genXY(pTreeList, negPList, sentiDict, wVolc, 
                p['keyTypeList'], p['opnNameList'], p['negSepList'], 
                p['minCnt'])
        volc = om.getVolc()
        rsList = RunExp.runTask(X, y, volc, 'AllTrainTest', p, clfList, topicMap=topicMap, 
                randSeedList=randSeedList)
        bestR = keepBestResult(bestR, rsList, 'MacroF1')
    with open('%s_%s_%s_AllTrainTest.pickle' %(modelName, dataset, wVolcPrefix), 'w+b') as f:
        pickle.dump(bestR, f)


    # ============= Run for leave-one-test ================
    print('Leave-One-Test...', file=sys.stderr)
    for t in topicSet:
        bestR = None
        for p in paramsIter:
            (X, y) = om.genXY(pTreeList, negPList, sentiDict, wVolc, 
                p['keyTypeList'], p['opnNameList'], p['negSepList'], 
                p['minCnt'])
            volc = om.getVolc()
            rsList = RunExp.runTask(X, y, volc, 'LeaveOneTest', p, clfList, 
                    topicMap=topicMap, topicId=t, randSeedList=randSeedList)
            bestR = keepBestResult(bestR, rsList, 'MacroF1', topicId=t)
        with open('%s_%s_%s_LeaveOneTest_topic%d.pickle' % (modelName, dataset, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)
          
