#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, csc_matrix, hstack
from sklearn.grid_search import ParameterGrid

from RunExperiments import *
from misc import *
from Volc import Volc

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
    def genXY(self, labelNewsList, feature='tf', volc=None, allowedPOS=None, minCnt=0):
        #initialization
        if volc == None:
            volc = Volc()
        IDF = None
        zeroOne = False
        if feature == '0/1' or feature == '01':
            zeroOne = True

        # calculate document frequency & generate volcabulary in advance
        (DF, volc) = WordModel.calcDF(labelNewsList, volc=volc)
        
        # remove the words whose document frequency <= threshold
        if minCnt != None:
            DF = volc.shrinkVolcByDocF(DF, minCnt)
        
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

        # get y
        y = np.array(getLabels(labelNewsList))
        
        # update volc
        self.volc = volc
        return (X, y)

    def getVolc(self):
        return self.volc

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
                    (word, tag) = wt.split(tagSep)
                    if word not in volc: # building volcabulary
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
def genXY(labelNewsList, wm, params, volc=None):
    print('generating word features...', file=sys.stderr)
    p = params
    (X, y) = wm.genXY(labelNewsList, feature=p['feature'], volc=volc, 
            allowedPOS=p['allowedPOS'], minCnt=p['minCnt'])
    volc = wm.getVolc()
    #print('X.shape:', X.shape)
    #print('volcSize:', len(volc))
    assert X.shape[1] == len(volc)
    return (X, y, volc)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:', sys.argv[0], 'TaggedLabelNewsJson modelConfigFile [volcFile]', file=sys.stderr)
        exit(-1)
    
    # arguments
    segLabelNewsJson = sys.argv[1]
    modelConfigFile = sys.argv[2]

    # load label  news 
    with open(segLabelNewsJson, 'r') as f:
        labelNewsList = json.load(f)
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)

    wVolc = None
    wVolcPrefix = ''
    if len(sys.argv) == 4:
        wVolcPrefix = getFileNamePrefix(sys.argv[3])
        wVolc = Volc()
        wVolc.load(sys.argv[3])
        wVolc.lock() # lock the volcabulary, new words are OOV

    # parameters:
    targetScore = config['setting']['targetScore']
    randSeedList = config['setting']['randSeedList']
    paramsIter = ParameterGrid(config['params'])
    clfList = config['setting']['clfList']
    modelName = config['setting']['modelName']
    dataset = config['setting']['dataset']

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabel(labelNewsList)

    # print first line of results
    ResultPrinter.printFirstLine()

    # initialize the model
    wm = WordModel()

    
    # ============= Run for self-train-test ===============
    print('Self-Train-Test...', file=sys.stderr)
    for t in topicSet:
        #if t != 2:
        #    continue
        bestR = None
        for p in paramsIter:
            (X, y, volc) = genXY(labelNewsInTopic[t], wm, p, volc=wVolc)
            rsList = RunExp.runTask(X, y, volc, 'SelfTrainTest', 
                    p, clfList, topicId=t, randSeedList=randSeedList)
            bestR = keepBestResult(bestR, rsList, targetScore)
        with open('%s_%s_%s_SelfTrainTest_topic%d.pickle' % (modelName, 
            dataset, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)

    # ============= Run for all-train-test & leave-one-test ================
    print('All-Train-Test & Leave-One-Test...', file=sys.stderr)
    bestR = None # for all-train-test
    bestR2 = {t:None for t in topicSet}  # for leave-one-test

    for p in paramsIter:
        (X, y, volc) = genXY(labelNewsList, wm, p, volc=wVolc)
        rsList = RunExp.runTask(X, y, volc, 'AllTrainTest', p, clfList, 
                topicMap=topicMap, randSeedList=randSeedList)
        bestR = keepBestResult(bestR, rsList, targetScore)
        for t in topicSet:
            rsList = RunExp.runTask(X, y, volc, 'LeaveOneTest', p, clfList, 
                    topicMap=topicMap, topicId=t, randSeedList=randSeedList)
            bestR2[t] = keepBestResult(bestR2[t], rsList, targetScore, topicId=t)

    with open('%s_%s_%s_AllTrainTest.pickle' %(modelName, dataset, wVolcPrefix), 'w+b') as f:
        pickle.dump(bestR, f)
        
    for t in topicSet:
        with open('%s_%s_%s_LeaveOneTest_topic%d.pickle' %(modelName, dataset, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR2[t], f)
