#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.grid_search import ParameterGrid

from RunExperiments import *
from misc import *

'''
This code implements the baseline (tf, tf-idf) features 
for training and testing (supervised document-level learning)
Author: Wei-Ming Chen
Date: 2015/02/16

'''

class WordModel:
    def __init__(self, labelNewsList, newsCols=['content'], statCol=False, feature='tf', volc=None):
        self.ln = labelNewsList
        self.newsCols = newsCols
        self.statCol = statCol
        self.feature = feature
        self.volc = volc

    def getVolc(self):
        return self.volc

    # convert the corpus of news to tf/tf-idf (a list of dict)
    def corpusToTFIDF(labelNewsList, column='content', IDF=None, volc=None, zeroOne=False):
        vectorList = list() # a list of dict()
        if volc == None:
            volc = dict() # vocabulary
        for labelNews in labelNewsList:
            if column == 'content':
                text = labelNews['news']['content_seg']
            elif column == 'title':
                text = labelNews['news']['title_seg']
            elif column == 'statement':
                text = labelNews['statement']['seg']
            vectorList.append(WordModel.text2TFIDF(text, IDF, volc, zeroOne))
        return (vectorList, volc)

    
    # convert text to TF-IDF features (dict)
    def text2TFIDF(text, IDF=None, volc=None, zeroOne=False, sentSep=",", wordSep=" "):
        f = dict()
        if volc == None:
            volc = dict()
        # term frequency 
        for sent in text.split(sentSep):
            for word in sent.split(wordSep):
                if word not in volc:
                    volc[word] = len(volc)
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

    # calculate inverse document frequency
    def calcIDF(labelNewsList, newsCols=['content'], sentSep=",", 
            wordSep=" ", volc=None):
        if volc == None:
            volc = dict()

        # calculating docuemnt frequency
        docF = defaultdict(int)
        for labelNews in labelNewsList:  
            wordSet = set()
            for col in newsCols:
                if col == 'title':
                    text = labelNews['news']['title_seg']
                elif col == 'content':
                    text = labelNews['news']['content_seg']
                for sent in text.split(sentSep):
                    for word in sent.split(wordSep):
                        if word not in volc: # building volcabulary
                            volc[word] = len(volc) 
                        wordSet.add(volc[word])
            for word in wordSet:
                docF[word] += 1

        # calculate IDF (log(N/(nd+1)))
        docNum = len(labelNewsList)
        IDF = dict()
        for key, value in docF.items():
            IDF[key] = math.log(float(docNum+1) / (value + 1))
        IDF['default'] = math.log(float(docNum+1))
        return (IDF, volc)

    def genXY(self):
        #initialization
        volc = self.volc
        if volc == None:
            volc = dict()
        
        IDF = None
        zeroOne = False
        if self.feature == '0/1' or self.feature == '01':
            zeroOne = True

        # calculate IDF 
        if self.feature == 'tfidf' or self.feature == 'tf-idf':
            (IDF, volc) = WordModel.calcIDF(self.ln, newsCols=self.newsCols, volc=volc)

        # calculate TF/TF-IDF (content / title)
        titleTFIDF = None # a list of dictionary, each dictionary is tf vector of one content
        contentTFIDF = None

        for col in self.newsCols:
            if col == 'title':
                (titleTFIDF, volc) = WordModel.corpusToTFIDF(self.ln, 
                        column='title', IDF=IDF, volc=volc, zeroOne=zeroOne)
            elif col == 'content':
                (contentTFIDF, volc) = WordModel.corpusToTFIDF(self.ln, 
                        column='content', IDF=IDF, volc=volc, zeroOne=zeroOne)
        newsTFIDF = listOfDictAdd(titleTFIDF, contentTFIDF)
        
        # calculate TF/TF-IDF (statement)
        statTFIDF = None
        if self.statCol:
            (statTFIDF, volc) = WordModel.corpusToTFIDF(self.ln, 
                    column='statement', IDF=IDF, volc=volc, zeroOne=zeroOne)
        
        # convert to CSR sparse matrix format
        X = convertToCSRMatrix(newsTFIDF, volc)
        if self.statCol:
            X2 = convertToCSRMatrix(statTFIDF, volc)
            X = csr_matrix(hstack((X, X2)))
            # expand volc (double it)
            tmpVolc = dict(volc)
            offset = len(volc)
            for v, i in tmpVolc.items():
                volc[v + '_stat'] = i + offset

        # get y
        y = np.array(getLabels(self.ln))
        
        # update volc
        self.volc = volc
        return (X, y)



def dictAdd(dict1, dict2):
    if dict1 == None:
        if dict2 == None:
            return None
        else:
            return dict2
    else:
        if dict2 == None:
            return dict1
    dict3 = dict()
    for key,value in dict1.items():
        if key not in dict3:
            dict3[key] = value
        else:
            dict3[key] += value
    for key,value in dict2.items():
        if key not in dict3:
            dict3[key] = value
        else:
            dict3[key] += value
    return dict3

def listOfDictAdd(listOfDict1, listOfDict2):
    if listOfDict1 == None:
        if listOfDict2 == None:
            return None
        else:
            return listOfDict2
    else:
        if listOfDict2 == None:
            return listOfDict1

    if len(listOfDict1) != len(listOfDict2):
        return None
        
    result = list()
    for i in range(0, len(listOfDict1)):
        dict1 = listOfDict1[i]
        dict2 = listOfDict2[i]
        dict3 = dictAdd(dict1, dict2)
        result.append(dict3)
        
    return result


def getLabels(labelNewsList):
    mapping = { "neutral" : 1, "oppose": 0, "agree" : 2 } 
    labelList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in mapping:
            labelList.append(mapping[labelNews['label']])
    return labelList

def convertToCSRMatrix(listOfDict, volc):
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
    m = csr_matrix((entries, (rows, cols)), 
            shape=(numRow, numCol), dtype=np.float64)
    return m

def divideLabel(labelNewsList):
    #FIXME stat and topic
    labelNewsInTopic = dict()
    for labelNews in labelNewsList:
        statId = labelNews['statement_id']
        if statId not in labelNewsInTopic:
            labelNewsInTopic[statId] = list()
        labelNewsInTopic[statId].append(labelNews)
    return labelNewsInTopic

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'segLabelNewsJson', file=sys.stderr)
        exit(-1)
    
    # arguments
    segLabelNewsJson = sys.argv[1]

    # load labels and news 
    with open(segLabelNewsJson, 'r') as f:
        labelNewsList = json.load(f)

    # print first line of results
    ResultPrinter.printFirstLine()

    # parameters:
    params = {
        'feature': ['0/1', 'tf', 'tfidf'],
        'col': [['content'], ['title'], ['title', 'content']],
        'stat': [False, True],
        'randSeed': [1, 2, 3, 4, 5]
    }
    clfList = ['NaiveBayes', 'MaxEnt', 'SVM' ]
    paramIter = ParameterGrid(params)

    # all topic are mixed to train and predict/ leave-one-test
    for p in paramIter:
        wm = WordModel(labelNewsList, newsCols=p['col'], 
                statCol=p['stat'], feature=p['feature'])
        (X, y) = wm.genXY()
                    
        prefix = 'all, %s, %s, %s, %s' % (p['feature'], '"None"', toStr(p['col']), p['stat'])
        topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
                    
        # all train and test
        RunExp.allTrainTest(X, y, topicMap, clfList, "MacroF1", 
                randSeed=p['randSeed'], testSize=0.2, prefix=prefix)
        # leave one test
        RunExp.leaveOneTest(X, y, topicMap, clfList, "MacroF1", 
                randSeed=p['randSeed'], prefix=prefix)
    
    # divide the news into different topic, each of them are trained and test by itself
    labelNewsInTopic = divideLabel(labelNewsList)
    for topicId, labelNewsList in labelNewsInTopic.items():
        for p in paramIter:
            wm = WordModel(labelNewsList, newsCols=p['col'], 
                    statCol=p['stat'], feature=p['feature'])
            (X, y) = wm.genXY()
                
            prefix = "%d, %s, %s, %s, %s" % (topicId, p['feature'], '"None"', toStr(p['col']), p['stat'])
            RunExp.selfTrainTest(X, y, clfList, 'MacroF1', 
                    randSeed=p['randSeed'], testSize=0.2, prefix=prefix)
    
