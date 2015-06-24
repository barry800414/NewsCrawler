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
import WordGraph

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
            if (i+1) % 100 == 0:
                print('%cIntializing the model... Progress: (%d/%d)' % (13, i+1, len(self.pln)), end='', file=sys.stderr)
        print('', file=sys.stderr)
    
    # copy original volcabulary
    def setVolcDict(self, volcDict):
        if volcDict is None:
            self.volcDict = { 'main': Volc(), 'seed': None, 'firstLayer': None }
        else:
            self.volcDict = dict()
            self.volcDict['main'] = Volc()
            if 'seed' in volcDict and volcDict['seed'] is not None:
                self.volcDict['seed'] = volcDict['seed'].copy()
            else:
                self.volcDict['seed'] = None

            if 'firstLayer' in volcDict and volcDict['firstLayer'] is not None:
                self.volcDict['firstLayer'] = volcDict['firstLayer'].copy()
            else:
                self.volcDict['firstLayer'] = None

        
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
    def genXY(self, allowedSeedWord, allowedSeedWordType, allowedFirstLayerWord, 
            allowedFirstLayerWordType, allowedRel, minCnt, volcDict, wordGraph, wgParams):
        self.asw = allowedSeedWord
        self.aswType = allowedSeedWordType
        self.aflw = allowedFirstLayerWord
        self.aflwType = allowedFirstLayerWordType
        self.ar = allowedRel
        self.minCnt = minCnt
        self.setModelFlag = True
        self.setVolcDict(volcDict) 
        self.wg = wordGraph
        self.wgParams = wgParams
        if self.wg is not None:
            assert self.volcDict['seed'] is not None and self.volcDict['firstLayer'] is not None
            assert len(self.volcDict['seed']) == len(self.volcDict['firstLayer']) 

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
        wordIndexSet = set()
        pairCntList = list()
        docF = defaultdict(int) # doc frequency for each pair
        for newsEdgeList in corpusEdgeList:
            pairCnt = self.extractPairs(newsEdgeList, wordIndexSet)
            for key in pairCnt.keys():
                docF[self.volcDict['main'][key]] += 1
            pairCntList.append(pairCnt)

        if wordGraph is not None and wgParams is not None:
            print('Doing word graph propagation ...', file=sys.stderr)
            print('# word index:', len(wordIndexSet), file=sys.stderr)
            nWords = len(self.volcDict['seed'])
            (S, mapping) = self.genIndexMatrix(wordIndexSet, nWords)
            # doing word propagation for each word in pairs
            # notice that this may be time consuming & need huge memory     
            nWordsPerDoc = [1 for i in range(0, len(wordIndexSet))]
            F = WordGraph.runWordGraphProp(S, wordGraph, wgParams['beta'], 
                    wgParams['step'], wgParams['method'], wgParams['value'], 
                    nWordsPerDoc)
            # for each document, update new pair count 
            newPairCntList = list()
            for i, pairCnt in enumerate(pairCntList):
                newPairCnt = defaultdict(float)
                for (si, fi), cnt in pairCnt.items():
                    # add new propagated pairs 
                    self.addNewPropPair(newPairCnt, cnt, F, si, fi, mapping)
                newPairCntList.append(newPairCnt)
                print(i+1, file=sys.stderr)
            pairCntList = newPairCntList

        # if the doc frequency of that pair is less than or equal 
        # to minCnt, then discard it
        #print('Pair volc size:', len(volc), end='', file=sys.stderr)
        #if self.minCnt != None:
        #    docF = self.volcDict['main'].shrinkVolcByDocF(docF, self.minCnt)
        #print('-> ', len(volc), file=sys.stderr)

        # converting all extraced dependencies to features X
        # Here the features are the word counts from each seed word, 
        # first layer word pair
        
        rows = list()
        cols = list()
        entries = list()
        for rowId, pairCnt in enumerate(pairCntList):
            for pairId, value in pairCnt.items():
                if pairId not in self.volcDict['main']:
                    self.volcDict['main'].addWord(pairId)
                colId = self.volcDict['main'][pairId]
                rows.append(rowId)
                cols.append(colId)
                entries.append(value)
        numRow = len(pairCntList)
        numCol = len(self.volcDict['main'])
        X = csr_matrix((entries, (rows, cols)), shape=(numRow, 
            numCol), dtype=np.float64)

        # remove the words whose document frequency <= threshold
        if minCnt != None:
            DF = countDFByCSRMatrix(X)
            X = shrinkCSRMatrixByDF(X, DF, minCnt)
            DF = self.volcDict['main'].shrinkVolcByDocF(DF, minCnt)

        y = np.array(getLabels(self.pln))

        return (X, y)

    def extractPairs(self, newsEdgeList, wordIndexSet):
        pairCnt = defaultdict(int)
        sVolc = self.volcDict['seed']
        fVolc = self.volcDict['firstLayer']
        mainVolc = self.volcDict['main']
        for edgeList in newsEdgeList:
            for rel,sP,sW,sT,eP,eW,eT in edgeList:
                if sVolc is not None and fVolc is not None:
                    # skip the words not in volcabulary
                    if sW not in sVolc or eW not in fVolc:
                        continue
                    pair = (sVolc[sW], fVolc[eW])
                    wordIndexSet.add(sVolc[sW])
                    wordIndexSet.add(fVolc[eW])
                else:
                    pair = (sW, eW)
                if pair not in mainVolc:
                    mainVolc.addWord(pair)
                pairCnt[pair] += 1
        return pairCnt

    def genIndexMatrix(self, wordIndexSet, nWords):
        rows = [i for i in range(0, len(wordIndexSet))]
        cols = sorted(list(wordIndexSet))
        mapping = {ci:i for i, ci in enumerate(cols) }
        data = [1 for i in range(0, len(wordIndexSet))]
        m = csr_matrix((data, (rows, cols)), shape=(len(wordIndexSet), nWords))
        
        return (m, mapping)
    
    # newPairCnt is a defaulctdict which stores the new pair count
    # cnt: the original count
    # F is a csr_matrix, each row represents the propogated result(words) of each word
    # si, fi are two original word index 
    # mapping is the mapping map original index to F's index
    # invMapping is the mapping map F's index to original index
    def addNewPropPair(self, newPairCnt, cnt, F, si, fi, mapping):
        si = mapping[si]
        fi = mapping[fi]
        m = F.getrow(si).transpose() * F.getrow(fi)
        (rowNum, colNum) = m.shape
        (colIndex, rowPtr, data) = m.indices, m.indptr, m.data
        nowPos = 0
        propPair = list()
        # traverse whole matrix 
        for ri in range(0, rowNum):
            for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
                prob = data[nowPos]
                newPairCnt[(ri, ci)] += cnt * prob
                nowPos += 1

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

def genXY(oldm, params, preprocess, minCnt, topicSet, sentiDict, volcDict, wordGraph, wgParams):
    print('generating one layer dependency features...', file=sys.stderr)
    p = params
    allowedSeedWord = initAllowedSet(topicSet, p['seedWordType'])
    allowedFirstLayerWord = initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
    allowedRel = { t: None for t in topicSet }
    (X, y) = oldm.genXY(allowedSeedWord, p['seedWordType']['type'], 
            allowedFirstLayerWord, p['firstLayerType']['type'], 
            allowedRel, minCnt, volcDict, wordGraph, wgParams)
    if preprocess != None:
        X = DataTool.preprocessX(X, preprocess['method'], preprocess['params'])
    volcDict = oldm.getVolcDict()
    assert X.shape[1] == len(volcDict['main'])
    return (X, y, volcDict)

def initOLDM(labelNewsList, topicPhraseList=None):
    oldm = OneLayerDepModel(labelNewsList, topicPhraseList)
    return oldm

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'DepParsedLabelNewsJson ModelConfig SentiDictFile', file=sys.stderr)
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

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)
    newsIdList = { t:[ln['news_id'] for ln in labelNewsInTopic[t]] for t in topicSet }
    newsIdList['All'] = [ln['news_id'] for ln in labelNewsList] 


    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    # load volcabulary file
    topicVolcDict = loadVolcFileFromConfig(config['volc'], topicSet)
    # load word graph
    (topicWordGraph, wgVolcDict, topicWGParams) = WordGraph.loadWordGraphFromConfig(config['wordGraph'], topicSet)
    if config['wordGraph'] is not None:
        topicVolcDict = wgVolcDict
    # load phrase file
    topicPhraseList = loadPhraseFileFromConfig(config['phrase'])

    # model parameters #FIXME: allowed relation
    toRun = config['toRun']
    taskName = config['taskName']
    preprocess = config['preprocess']
    minCnt = config['minCnt']
    setting = config['setting']
    targetScore = config['setting']['targetScore'] 
    paramsIter = ParameterGrid(config['params'])

    ResultPrinter.printFirstLine()

    # intialize the model
    if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
        #oldm = initOLDM(labelNewsList, topicPhraseList)
        pass
    if 'SelfTrainTest' in toRun:
        toldm = { t: initOLDM(ln, topicPhraseList) for t, ln in labelNewsInTopic.items() if t==3}
 
    # ============= Run for self-train-test ===============
    if 'SelfTrainTest' in toRun:
        print('Self-Train-Test...', file=sys.stderr)
        for t in topicSet:
            if t != 3:
                continue
            for p in paramsIter:
                (X, y, newVolcDict) = genXY(toldm[t], p, preprocess, minCnt, topicSet, sentiDict, topicVolcDict[t], 
                        topicWordGraph[t], topicWGParams[t])
                expLog = RunExp.runTask(X, y, newVolcDict, newsIdList[t], 'SelfTrainTest', p, topicId=t, **setting)
            with open('%s_SelfTrainTest_topic%d.pickle' % (taskName, t), 'w+b') as f:
                pickle.dump(expLog, f)

    # ============= Run for all-train-test & leave-one-test ================
    print('All-Train-Test & Leave-One-Test...', file=sys.stderr)
    for p in paramsIter:
        if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
            (X, y, newVolcDict) = genXY(oldm, p, preprocess, minCnt, topicSet, sentiDict, topicVolcDict['All'], 
                        topicWordGraph['All'], topicWGParams['All'])
        if 'AllTrainTest' in toRun:
            expLog = RunExp.runTask(X, y, newVolcDict, newsIdList['All'], 'AllTrainTest', p, topicMap=topicMap, **setting)
            with open('%s_AllTrainTest.pickle' %(taskName), 'w+b') as f:
                pickle.dump(expLog, f)
        if 'LeaveOneTest' in toRun:
            for t in topicSet:
                expLog = RunExp.runTask(X, y, newVolcDict, newsIdList['All'], 'LeaveOneTest', p, topicMap=topicMap, topicId=t, **setting)
                with open('%s_LeaveOneTest_topic%d.pickle' %(taskName, t), 'w+b') as f:
                    pickle.dump(expLog, f)
