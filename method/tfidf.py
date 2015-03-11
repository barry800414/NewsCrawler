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
    return csr_matrix((entries, (rows, cols)), 
            shape=(numRow, numCol), dtype=np.float64)

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
        IDF[key] = math.log(float(docNum) / (value + 1))
    IDF['default'] = math.log(float(docNum))
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
        X = hstack((X, X2))
    
    # get y
    y = np.array(getLabels(labelNewsList))
    
    return (X, y)

def trainingAndTesting(X_train, X_test, y_train, y_test, classifier='SVM', prefix=None):

    if classifier == 'NaiveBayes':
        clf = MultinomialNB()
        clf.fit(X_train, y_train)
        print(prefix,'testing', 'MultinomialNB', clf.score(X_test, y_test), sep=',')
        #clf2 = GaussianNB()
        #clf2.fit(X_train, y_train)
        #print('testing', 'GaussianNB', clf2.score(X_test, y_test), sep=',')
        return 

    elif classifier == 'SVM':
        # grid search to find best parameters on training set
        C = [math.pow(2, i) for i in range(-5,15,2)]
        gamma = [math.pow(2, i) for i in range(-15,3,2)]
        parameters = {
                'kernel': ('rbf', 'linear'), 
                'C': C, 
                'gamma': gamma
            }
        clf = svm.SVC()
    
    elif classifier == 'RandomForest': #depricated: RF does not support sparse matrix
        estNum = [5, 10, 15, 20]
        minSampleSplit = [1, 2]
        parameters = {
                "n_estimators": estNum,
                "min_samples_split": minSampleSplit
            }
        clf = RandomForestClassifier()

    
    # if not naive Bayes:
    clfGS = grid_search.GridSearchCV(clf, parameters, refit=True, n_jobs=-1)
    clfGS.fit(X_train, y_train)
        
    #for gs in clfGS.grid_scores_:
        #print(prefix,'validation', gs[0], np.mean(gs[2]), sep=',')    

    # testing 
    print(prefix,'testing', clfGS.best_params_, clfGS.score(X_test, y_test), sep=',')
    


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'segLabelNewsJson', file=sys.stderr)
        exit(-1)
    
    # arguments
    segLabelNewsJson = sys.argv[1]

    # load labels and news 
    with open(segLabelNewsJson, 'r') as f:
        labelNewsList = json.load(f)

    # cleaning the data 
    labelNewsList = dataPreprocess.data_cleaning(labelNewsList, printInfo=True)

    # print statiscal information
    dataPreprocess.printStatInfo(labelNewsList)

    # print results
    print('columnSource, statementCol, classifier, val_or_test, parameters, accuarcy')

    # main loop for running experiments
    # generating X and y
    cnt = 0
    featureList = ['tf', 'tfidf']
    colsList = [['content'], ['title'], ['title', 'content']]
    statList = [False, True]
    clfList = [ 'NaiveBayes', 'SVM']
    taskNum = len(featureList) * len(colsList) * len(statList) * len(clfList)
    for feature in featureList:
        for newsCols in colsList:
            for statementCol in statList:
                (X, y) = generateXY(labelNewsList, newsCols=newsCols, 
                        statementCol=statementCol, feature=feature)

                (X_train, X_test, y_train, y_test) = cross_validation.train_test_split(
                        X, y, test_size=0.5, random_state=1)
                
                for classifier in clfList:
                    prefix = "%s, %s, %s, %s" % (feature, newsCols, statementCol, classifier)
                    trainingAndTesting(X_train, X_test, y_train, y_test, classifier, prefix)
                    cnt += 1
                    print('Progress: (%d/%d)' % (cnt, taskNum), file=sys.stderr)
                    

