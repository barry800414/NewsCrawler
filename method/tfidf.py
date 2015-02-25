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

'''
This code implements the baseline (tf, tf-idf) features 
for training and testing (supervised document-level learning)
Author: Wei-Ming Chen
Date: 2015/02/16

'''

def data_cleaning(labelNewsList, printInfo=False):
    labelSet = set(["neutral", "oppose", "agree"])
    newList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in labelSet:
            newList.append(labelNews)
    return newList

# convert the contents of news to term frequency features
def convertToTFFeatures(labelNewsList, column='content', volc=None):
    vectorList = list() # a list of dict()
    if volc == None:
        volc = dict() # vocabulary
    for labelNews in labelNewsList:
        if column == 'content':
            content = labelNews['news']['content_seg']
        elif column == 'title':
            content = labelNews['news']['title_seg']
        elif column == 'statement':
            content = labelNews['statement_seg']
        vectorList.append(__toTF(content, volc))
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

def __toTF(content, volc=None, sentSep=",", wordSep=" "):
    vector = defaultdict(int)
    if volc == None:
        volc = dict()
    for sent in content.split(sentSep):
        for word in sent.split(wordSep):
            if word not in volc:
                volc[word] = len(volc)
            vector[volc[word]] += 1
    return vector

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


def generateXY(labelNewsList, newsCols=['content'], statementCol=False, 
        features=['tf'], testRatio=0.5):

    # convert to term frequency features (content / title)
    titleTF = None # a list of dictionary, each dictionary is tf vector of one content
    contentTF = None
    volc = dict() # vocabulary

    for col in newsCols:
        if col == 'title':
            (titleTF, volc) = convertToTFFeatures(labelNewsList, 
                    column='title', volc=volc)
        elif col == 'content':
            (contentTF, volc) = convertToTFFeatures(labelNewsList, 
                    column='content', volc=volc)
    newsTF = __listOfDictAdd(titleTF, contentTF)

    # convert to term frequency features (statement)
    statementTF = None
    if statementCol:
        (statementTF, volc) = convertToTFFeatures(labelNewsList, 
                column='statement', volc=volc)
    
    # convert to CSR sparse matrix format
    X = convertToCSRMatrix(newsTF, volc)
    if statementCol:
        X2 = convertToCSRMatrix(statementTF, volc)
        X = hstack(X, X2)
    
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


def printStatInfo(labelNewsList):
    statSet = set() 
    for labelNews in labelNewsList:
        statSet.add(labelNews['statement_id'])

    num = dict()
    for statId in statSet:
        num[statId] = { "agree": 0, "oppose": 0, "neutral": 0 }
    
    for labelNews in labelNewsList:
        num[labelNews['statement_id']][labelNews['label']] += 1

    agreeSum = 0
    neutralSum = 0
    opposeSum = 0
    for statId in statSet:
        agree = num[statId]['agree']
        neutral = num[statId]['neutral']
        oppose = num[statId]['oppose']
        total = agree + neutral + oppose
        print('Statement %d: agree/neutral/oppose: %d/%d/%d (%f/%f/%f)' % (statId, 
             agree, neutral, oppose, float(agree)/total, float(neutral)/total, 
             float(oppose)/total), file=sys.stderr)
        agreeSum += agree
        neutralSum += neutral
        opposeSum += oppose
    totalSum = agreeSum + neutralSum + opposeSum
    print('Total: agree/neutral/oppose: %d/%d/%d (%f/%f/%f)' % (agreeSum, neutralSum,
        opposeSum, float(agreeSum)/totalSum, float(neutralSum)/totalSum, 
             float(opposeSum)/totalSum), file=sys.stderr)

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
    labelNewsList = data_cleaning(labelNewsList, printInfo=True)

    # print statiscal information
    printStatInfo(labelNewsList)

    # print results
    print('columnSource, statementCol, classifier, val_or_test, parameters, accuarcy')

    # main loop for running experiments
    # generating X and y
    cnt = 0
    colsList = [['content'], ['title'], ['title', 'content']]
    statList = [False]
    clfList = [ 'NaiveBayes', 'SVM']
    taskNum = len(colsList) * len(statList) * len(clfList)
    for newsCols in colsList:
        for statementCol in statList:
            (X, y) = generateXY(labelNewsList, newsCols=newsCols, 
                    statementCol=statementCol, features=['tf'])

            (X_train, X_test, y_train, y_test) = cross_validation.train_test_split(
                    X, y, test_size=0.5, random_state=1)
            
            for classifier in clfList:
                prefix = "%s, %s, %s" % (newsCols, statementCol, classifier)
                trainingAndTesting(X_train, X_test, y_train, y_test, classifier, prefix)
                cnt += 1
                print('Progress: (%d/%d)' % (cnt, taskNum), file=sys.stderr)
                

