#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import scipy.io
import numpy as np
from scipy.sparse import csr_matrix, csc_matrix, hstack
from sklearn.grid_search import ParameterGrid

from RunExperiments import *
from misc import *
from Volc import *
import WordGraph

'''
This is the improved version of WordModel
 1.remove < 1 dimension (DONE)
 2.allowed some of pos taggers (DONE)
 3.word clustering 
 4.highest tfidf

Author: Wei-Ming Chen
Date: 2015/05/04

'''

class WordModel:
    def genXY(self, labelNewsList, feature='tf', volcDict=None, allowedPOS=None, 
            minCnt=0, wordGraph=None, wgParams=None):
        self.setVolcDict(volcDict)
        volc = self.volcDict['main']
        IDF = None
        zeroOne = False
        if feature == '0/1' or feature == '01':
            zeroOne = True

        # calculate document frequency & generate volcabulary in advance
        (DF, volc) = WordModel.calcDF(labelNewsList, volc=volc)
        
        # remove the words whose document frequency <= threshold
        #if minCnt != None:
        #    DF = volc.shrinkVolcByDocF(DF, minCnt)
        
        # calcualte IDF if necessary
        if feature == 'tfidf' or feature == 'tf-idf':
            IDF = WordModel.DF2IDF(DF, len(labelNewsList))
        
        # calculate TF/TF-IDF (content)
        newsTFIDF = None
        (newsTFIDF, volc) = WordModel.corpusToTFIDF(labelNewsList,
                        allowedPOS=allowedPOS, IDF=IDF, volc=volc, 
                        zeroOne=zeroOne)
        
        # generate X
        X = toMatrix(newsTFIDF, volc, matrixType='csr')
        # if word graph is given, then run word graph propagation algorithm
        if wordGraph is not None and wgParams is not None:
            print('Doing word graph propagation ...', file=sys.stderr)
            nWordsPerDoc = [len(tfidf) for tfidf in newsTFIDF]
            X = WordGraph.runWordGraphProp(X, wordGraph, wgParams['beta'], wgParams['step'], 
                    wgParams['method'], wgParams['value'], nWordsPerDoc)

        # remove the words whose document frequency <= threshold
        if minCnt != None:
            DF = countDFByCSRMatrix(X)
            X = shrinkCSRMatrixByDF(X, DF, minCnt)
            DF = volc.shrinkVolcByDocF(DF, minCnt)

        # get y
        y = np.array(getLabels(labelNewsList))
        
        # update volc
        self.volcDict['main'] = volc

        return (X, y)

    # copy original volcabulary
    def setVolcDict(self, volcDict):
        if volcDict is None:
            self.volcDict = { 'main': None }
        else:
            self.volcDict = dict()
            self.volcDict['main'] = volcDict['main'].copy()

    def getVolcDict(self):
        return self.volcDict

    # convert the corpus of news to tf/tf-idf (a list of dict)
    def corpusToTFIDF(labelNewsList, volc, allowedPOS=None, IDF=None, zeroOne=False):
        vectorList = list() # a list of dict()
        for labelNews in labelNewsList:
            text = labelNews['news']['content_pos']
            vectorList.append(WordModel.text2TFIDF(text, volc, 
                allowedPOS, IDF, zeroOne))
        return (vectorList, volc)

    # convert text to TF-IDF features (dict)
    def text2TFIDF(text, volc, allowedPOS=None, IDF=None, zeroOne=False, 
            sentSep=",", wordSep=" ", tagSep='/'):
        f = dict()
        # term frequency 
        for sent in text.split(sentSep):
            for wt in sent.split(wordSep):
                (word, tag) = wt.split(tagSep)
                if allowedPOS != None and tag not in allowedPOS:
                    continue
                if word not in volc:
                    continue
                
                if volc[word] not in f:
                    f[volc[word]] = 1
                else:
                    if not zeroOne: #if not zeroOne, calculate the count
                        f[volc[word]] += 1
                    
        # if idf is given, then calculate tf-idf
        if IDF != None:
            for key, value in f.items():
                if key not in IDF:
                    #print('Document Frequency Error', file=sys.stderr)
                    f[key] = value * IDF['default']
                else:
                    f[key] = value * IDF[key]

        return f

    # calculate document frequency
    def calcDF(labelNewsList, sentSep=",", wordSep=" ", tagSep='/', volc=None):
        if volc == None:
            volc = Volc()
        # calculating docuemnt frequency
        docF = defaultdict(int)
        for labelNews in labelNewsList:
            wordIdSet = set()
            text = labelNews['news']['content_pos']
            for sent in text.split(sentSep):
                for wt in sent.split(wordSep):
                    #print(wt)
                    (word, tag) = wt.split(tagSep)
                    if word not in volc and not volc.lockVolc: # building volcabulary
                        volc.addWord(word)
                        wordIdSet.add(volc[word])

            for word in wordIdSet:
                docF[word] += 1
        return (docF, volc)

    # convert document frequency to inverse document frequency
    def DF2IDF(DF, docNum):
        # calculate IDF (log(N/(nd+1)))
        IDF = dict()
        for key, value in DF.items():
            IDF[key] = math.log(float(docNum+1) / (value + 1))
        IDF['default'] = math.log(float(docNum+1))
        return IDF


def toMatrix(listOfDict, volc, matrixType='csr'):
    rows = list()
    cols = list()
    entries = list()
    for rowId, dictObject in enumerate(listOfDict):
        for colId, value in dictObject.items():
            rows.append(rowId)
            cols.append(colId)
            entries.append(value)
    numRow = len(listOfDict)
    numCol = len(volc)
    if matrixType == 'csr':
        m = csr_matrix((entries, (rows, cols)), 
                shape=(numRow, numCol), dtype=np.float64)
    elif matrixType == 'csc':
        m = csc_matrix((entries, (rows, cols)), 
                shape=(numRow, numCol), dtype=np.float64)
    else:
        m = None
    return m

def initWM():
    return WordModel()

# generate word model features
def genXY(labelNewsList, wm, params, preprocess, minCnt, volcDict, wordGraph, wgParams):
    print('generating word features...', file=sys.stderr)
    p = params
    (X, y) = wm.genXY(labelNewsList, feature=p['feature'], volcDict=volcDict, 
            allowedPOS=p['allowedPOS'], minCnt=minCnt, wordGraph=wordGraph, wgParams=wgParams)
    if preprocess != None:
        X = DataTool.preprocessX(X, preprocess['method'], preprocess['params'])
    volcDict = wm.getVolcDict()
    assert X.shape[1] == len(volcDict['main'])
    return (X, y, volcDict)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'TaggedLabelNewsJson modelConfigFile', file=sys.stderr)
        exit(-1)
    
    # arguments
    segLabelNewsJson = sys.argv[1]
    modelConfigFile = sys.argv[2]

    # load label news 
    with open(segLabelNewsJson, 'r') as f:
        labelNewsList = json.load(f)
    # load model config
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)
    newsIdList = { t:[ln['news_id'] for ln in labelNewsInTopic[t]] for t in topicSet }
    newsIdList['All'] = [ln['news_id'] for ln in labelNewsList] 

    # sample document if neccessary
    labelNewsList = runSampleDoc(labelNewsList, config)

    # load volcabulary file
    topicVolcDict = loadVolcFileFromConfig(config['volc'], topicSet)
    # load word graph
    (topicWordGraph, wgVolcDict, topicWGParams) = WordGraph.loadWordGraphFromConfig(config['wordGraph'], topicSet)
    if config['wordGraph'] is not None:
        topicVolcDict = wgVolcDict

    # parameters:
    #print(config, file=sys.stderr)
    toRun = config['toRun']
    taskName = config['taskName']
    preprocess = config['preprocess']
    minCnt = config['minCnt']
    setting = config['setting']
    targetScore = config['setting']['targetScore'] 
    paramsIter = ParameterGrid(config['params'])

    # print first line of results
    ResultPrinter.printFirstLine()

    # initialize the model
    wm = WordModel()

    # ============= Run for self-train-test ===============
    if 'SelfTrainTest' in toRun:
        print('Self-Train-Test...', file=sys.stderr)
        for t in topicSet:
            for p in paramsIter:
                (X, y, newVolcDict) = genXY(labelNewsInTopic[t], wm, p, preprocess, minCnt, 
                        topicVolcDict[t], topicWordGraph[t], topicWGParams[t])
                expLog = RunExp.runTask(X, y, newVolcDict, newsIdList[t], 'SelfTrainTest', p, topicId=t, **setting)
            with open('%s_SelfTrainTest_topic%d.pickle' % (taskName, t), 'w+b') as f:
                pickle.dump(expLog, f)

    # ============= Run for all-train-test & leave-one-test ================
    for p in paramsIter:
        if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
            (X, y, newVolcDict) = genXY(labelNewsList, wm, p, preprocess, minCnt, topicVolcDict['All'], topicWordGraph['All'], topicWGParams['All'])
        
        if 'AllTrainTest' in toRun:
            expLog = RunExp.runTask(X, y, newVolcDict, newsIdList['All'], 'AllTrainTest', p, topicMap=topicMap, **setting)
            with open('%s_AllTrainTest.pickle' %(taskName), 'w+b') as f:
                pickle.dump(expLog, f)
        
        if 'LeaveOneTest' in toRun:
            for t in topicSet:
                expLog = RunExp.runTask(X, y, newVolcDict, newsIdList['All'], 'LeaveOneTest', p, topicMap=topicMap, 
                        topicId=t, **setting)
                with open('%s_LeaveOneTest_topic%d.pickle' %(taskName, t), 'w+b') as f:
                    pickle.dump(expLog, f)
