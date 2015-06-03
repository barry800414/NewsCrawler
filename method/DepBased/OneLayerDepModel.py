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
from misc import *
from Volc import Volc
from misc import *

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
    # wVolc: word vocabulary
    def __init__(self, depParsedLabelNews, topicPhraseList=None, wVolc=None):
        self.pln = depParsedLabelNews
        self.topicPhraseList = topicPhraseList
        self.wVolc = wVolc # word vocabulary
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
    def getVolc(self):
        return self.volc
    
    # the word volc
    def getWordVolc(self):
        return self.wVolc

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
    def genXY(self, allowedSeedWord, allowedSeedWordType, 
            allowedFirstLayerWord, allowedFirstLayerWordType, 
            allowedRel, minCnt=0, debugLevel=0, debugFile=sys.stderr):
        self.asw = allowedSeedWord
        self.aswType = allowedSeedWordType
        self.aflw = allowedFirstLayerWord
        self.aflwType = allowedFirstLayerWordType
        self.ar = allowedRel
        self.minCnt = minCnt
        self.debugLevel = debugLevel
        self.debugFile = debugFile
        self.setModelFlag = True
        self.volc = None # pair vocabulary


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
                edgeList = dg.searchOneStep()
                
                # save all the searched depenencies for later usage
                newsEdgeList.append(edgeList)

            # corpusEdgeList[newsIndex][depGraphIndex][edgeIndex]
            corpusEdgeList.append(newsEdgeList)

        # build the volcabulary for pair
        volc = self.volc if self.volc != None else Volc()
        wVolc = self.wVolc
        
        pairCntList = list()
        docF = defaultdict(int) # doc frequency for each pair
        for newsEdgeList in corpusEdgeList:
            pairCnt = self.extractPairs(newsEdgeList, wVolc, volc)
            for key in pairCnt.keys():
                docF[volc[key]] += 1
            pairCntList.append(pairCnt)

        # if the doc frequency of that pair is less than or equal 
        # to minCnt, then discard it
        #print('Pair volc size:', len(volc), end='', file=sys.stderr)
        if self.minCnt != None:
            docF = volc.shrinkVolcByDocF(docF, self.minCnt)
        #print('-> ', len(volc), file=sys.stderr)

        # converting all extraced dependencies to features X
        # Here the features are the word counts from each seed word, 
        # first layer word pair
        
        rows = list()
        cols = list()
        entries = list()
        for rowId, pairCnt in enumerate(pairCntList):
            for pairId, value in pairCnt.items():
                if pairId not in volc:
                    continue
                colId = volc[pairId]
                rows.append(rowId)
                cols.append(colId)
                entries.append(value)
        numRow = len(pairCntList)
        numCol = len(volc)
        X = csr_matrix((entries, (rows, cols)), shape=(numRow, 
            numCol), dtype=np.float64)
        y = np.array(getLabels(self.pln))

        # update volcabulary
        self.wVolc = wVolc
        self.volc = volc

        return (X, y)

    def extractPairs(self, newsEdgeList, wVolc, volc):
        pairCnt = defaultdict(int)
        for edgeList in newsEdgeList:
            for rel,sP,sW,sT,eP,eW,eT in edgeList:
                if wVolc != None:
                    wVolc.addWord(sW)
                    wVolc.addWord(eW)
                    pair = (wVolc[sW], wVolc[eW])
                else:
                    pair = (sW, eW)
                if pair not in volc:
                    volc.addWord(pair)
                pairCnt[pair] += 1
        return pairCnt


# add a set of word to volcabulary
def addWordSetToVolc(wordSet, volc):
    for w in wordSet:
        if w not in volc:
            volc.addWord(w)
        
# initialize allowed set. dictionary: word -> score
def initAllowedSet(topicSet, config, dictionary=None):
    if config['type'] == 'word': #using words in dictionary
        allowedSet = { topicId: set(dictionary.keys()) for topicId in topicSet }
    elif config['type'] == 'tag': #using tag
        allowedSet = { topicId: set(config['allow']) for topicId in topicSet }
    return allowedSet

def genXY(oldm, params, preprocess, minCnt, topicSet, sentiDict):
    print('generating one layer dependency features...', file=sys.stderr)
    p = params
    allowedSeedWord = initAllowedSet(topicSet, p['seedWordType'])
    allowedFirstLayerWord = initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
    allowedRel = { t: None for t in topicSet }
    (X, y) = oldm.genXY(allowedSeedWord, p['seedWordType']['type'], 
            allowedFirstLayerWord, p['firstLayerType']['type'], 
            allowedRel, minCnt)
    if preprocess != None:
        X = DataTool.preprocessX(X, preprocess['method'], preprocess['params'])
    volc = oldm.getVolc()
    wVolc = oldm.getWordVolc()
    assert X.shape[1] == len(volc)
    return (X, y, volc, wVolc)

def initOLDM(labelNewsList, topicPhraseList=None, wVolc=None):
    oldm = OneLayerDepModel(labelNewsList, topicPhraseList, wVolc)
    return oldm

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:', sys.argv[0], 'DepParsedLabelNewsJson ModelConfig SentiDictFile [-p phraseFile] [-v volcFile]', file=sys.stderr)
        exit(-1)

    depParsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    modelConfigFile = sys.argv[2]
    sentiDictFile = sys.argv[3]

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

    # load other files
    topicPhraseList = None
    wVolc = None
    wVolcPrefix = ''
    for i in range(4, len(sys.argv)):
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
            wVolc.lock() # lock the volcabulary, all new words are viewed as OOV
            i = i + 1

    # model parameters #FIXME: allowed relation
    toRun = config['toRun']
    modelName = config['modelName']
    dataset = config['dataset']
    preprocess = config['preprocess']
    minCnt = config['minCnt']
    setting = config['setting']
    targetScore = config['setting']['targetScore'] 

    paramsIter = ParameterGrid(config['params'])

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)

    ResultPrinter.printFirstLine()

    # intialize the model
    if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
        oldm = initOLDM(labelNewsList, topicPhraseList, wVolc)
    
    if 'SelfTrainTest' in toRun:
        toldm = { t: initOLDM(ln, topicPhraseList, wVolc) for t, ln in labelNewsInTopic.items()}
 
    # ============= Run for self-train-test ===============
    if 'SelfTrainTest' in toRun:
        print('Self-Train-Test...', file=sys.stderr)
        for t in topicSet:
            #if t != 2:
            #    continue
            bestR = None
            for p in paramsIter:
                (X, y, volc, wVolc) = genXY(toldm[t], p, preprocess, minCnt, topicSet, sentiDict)
                rsList = RunExp.runTask(X, y, volc, 'SelfTrainTest', p, topicId=t, wVolc=wVolc, **setting)
                bestR = keepBestResult(bestR, rsList, targetScore)
            with open('%s_%s_%s_SelfTrainTest_topic%d.pickle' % (modelName, dataset, wVolcPrefix, t), 'w+b') as f:
                pickle.dump(bestR, f)

    # ============= Run for all-train-test & leave-one-test ================
    print('All-Train-Test & Leave-One-Test...', file=sys.stderr)
    bestR = None # for all-train-test
    bestR2 = {t:None for t in topicSet}  # for leave-one-test

    for p in paramsIter:
        if 'AllTrainTest' in toRun:
            (X, y, volc, wVolc) = genXY(oldm, p, preprocess, minCnt, topicSet, sentiDict)
            rsList = RunExp.runTask(X, y, volc, 'AllTrainTest', p, topicMap=topicMap, wVolc=wVolc, **setting)
            bestR = keepBestResult(bestR, rsList, targetScore)
        if 'LeaveOneTest' in toRun:
            for t in topicSet:
                rsList = RunExp.runTask(X, y, volc, 'LeaveOneTest', p, topicMap=topicMap, topicId=t, wVolc=wVolc, **setting)
                bestR2[t] = keepBestResult(bestR2[t], rsList, targetScore, topicId=t)
    
    if 'AllTrainTest' in toRun:
        with open('%s_%s_%s_AllTrainTest.pickle' %(modelName, dataset, wVolcPrefix), 'w+b') as f:
            pickle.dump(bestR, f)
    
    if 'LeaveOneTest' in toRun:
        for t in topicSet:
            with open('%s_%s_%s_LeaveOneTest_topic%d.pickle' %(modelName, dataset, wVolcPrefix, t), 'w+b') as f:
                pickle.dump(bestR2[t], f)
