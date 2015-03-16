#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn import svm, cross_validation, grid_search
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB

import dataPreprocess
import MLProcedure
from misc import *

'''
This code implements the baseline (tf, tf-idf) features 
for training and testing (supervised document-level learning)
Author: Wei-Ming Chen
Date: 2015/02/16

'''

# convert the contents of news to tf/tf-idf (a list of dict)
def convertToTFIDF(labelNewsList, column='content', IDF=None, volc=None):
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
        vectorList.append(sentToTFIDF(text, IDF, volc))
    return (vectorList, volc)

def __dictAdd(dict1, dict2):
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

def __listOfDictAdd(listOfDict1, listOfDict2):
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
        dict3 = __dictAdd(dict1, dict2)
        result.append(dict3)
        
    return result

# convert sentence to TF-IDF features (dict)
def sentToTFIDF(text, IDF=None, volc=None, sentSep=",", wordSep=" "):
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

def generateXY(labelNewsList, newsCols=['content'], statementCol=False, 
        feature='tf'):

    #initialization
    volc = dict()
    IDF = None

    # calculate IDF 
    if feature == 'tfidf' or feature == 'tf-idf':
        (IDF, volc) = calcIDF(labelNewsList, newsCols=newsCols, volc=volc)

    # calculate TF/TF-IDF (content / title)
    titleTFIDF = None # a list of dictionary, each dictionary is tf vector of one content
    contentTFIDF = None

    for col in newsCols:
        if col == 'title':
            (titleTFIDF, volc) = convertToTFIDF(labelNewsList, 
                    column='title', IDF=IDF, volc=volc)
        elif col == 'content':
            (contentTFIDF, volc) = convertToTFIDF(labelNewsList, 
                    column='content', IDF=IDF, volc=volc)
    newsTFIDF = __listOfDictAdd(titleTFIDF, contentTFIDF)
    
    # calculate TF/TF-IDF (statement)
    statementTFIDF = None
    if statementCol:
        (statementTFIDF, volc) = convertToTFIDF(labelNewsList, 
                column='statement', IDF=IDF, volc=volc)
    
    # convert to CSR sparse matrix format
    X = convertToCSRMatrix(newsTFIDF, volc)
    if statementCol:
        X2 = convertToCSRMatrix(statementTFIDF, volc)
        X = csr_matrix(hstack((X, X2)))
    
    # get y
    y = np.array(getLabels(labelNewsList))
    
    return (X, y)


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

    # print statiscal information
    dataPreprocess.printStatInfo(labelNewsList)

    # print results
    print('topicId, feature, columnSource, statementCol, ', 
            'classifier, val_or_test, parameters, scorer, ',
            'accuracy, macroF1, microF1, macroR', sep='')

    # main loop for running experiments
    # generating X and y
    cnt = 0
    featureList = ['tf', 'tfidf']
    colsList = [['content'], ['title'], ['title', 'content']]
    statList = [False, True]
    clfList = ['NaiveBayes', 'MaxEnt', 'SVM' ]
    
    # all news are mixed to train and predict
    '''
    for feature in featureList:
        for newsCols in colsList:
            for statementCol in statList:
                (X, y) = generateXY(labelNewsList, newsCols=newsCols, 
                       statementCol=statementCol, feature=feature)
                
                prefix = "all, %s, %s, %s" % (feature, list2Str(newsCols), statementCol)
                #FIXME topicMapping or statMapping??
                topicMapping = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
                MLProcedure.runExperiments(X, y, topicMapping, clfList=clfList, prefix=prefix)
    '''
        
    # divide the news into different topic, each of them are trained and test by itself
    labelNewsInTopic = divideLabel(labelNewsList)
    for topicId, labelNewsList in labelNewsInTopic.items():
        for feature in featureList:
            for newsCols in colsList:
                for statementCol in statList:
                    (X, y) = generateXY(labelNewsList, newsCols=newsCols, 
                       statementCol=statementCol, feature=feature)
                
                    prefix = "%d, %s, %s, %s" % (topicId, feature, list2Str(newsCols), statementCol)
                    MLProcedure.runExperiments(X, y, clfList=clfList, prefix=prefix)

