#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.grid_search import ParameterGrid

import WordModel as WM
import OneLayerPhraseDepModel as OLPDM
from PhraseDepTree import loadPhraseFile
from sentiDictSum import readSentiDict
from RunExperiments import *
import ErrorAnalysis as EA
from misc import *
import dataTool
import Parameter

'''
This code implements the baseline (tf, tf-idf) features 
for training and testing (supervised document-level learning)
Author: Wei-Ming Chen
Date: 2015/02/16

'''

# Depricated
def mainProcedure(labelNewsList, paramsIter, clfList, allowedFirstLayerWord, 
        allowedRel, topicMap=None, topicId=None):
    oldms = dict()
    for p in paramsIter:
        # generate tfidf features
        print('generating tfidf features...', file=sys.stderr)
        (X1, y1) = tfidf.generateXY(labelNewsList, newsCols=p['columnSource'], 
                       statCol=p['statementCol'], feature=p['feature'])
        print('X1: (%d, %d)' % (X1.shape[0], X1.shape[1]), file=sys.stderr)

        # generate OLPDM features
        print('generating OLPDM features...', file=sys.stderr)

        # saving model for speed up
        if p['seedWordPOSType'] not in oldms:
            allowedSeedWord = { topicId: set(p['seedWordPOSType']) for topicId in topicSet }
            oldm = OLPDM.OneLayerPhraseDepModel(labelNewsList, topicPhraseList, allowedSeedWord, 
                'tag', allowedFirstLayerWord, 'word', allowedRel)
            oldms[p['seedWordPOSType']] = oldm
        else:
            oldm = oldms[p['seedWordPOSType']]

        (X2, y2) = oldm.genXY()
        print('X2: (%d, %d)' % (X2.shape[0], X2.shape[1]), file=sys.stderr)

        # merge (horozontally align) two matrix
        X = DataTool.hstack(X1, X2)
        print('X: %d %d' % (X.shape[0], X.shape[1]), file=sys.stderr)
        
        if topicMap == None: #self train -> self test
            prefix = "%d, %s, %s, %s" % (topicId, 'OLPDM+' + str(p['feature']), 
                    toStr(p['columnSource']), p['statementCol'])
            RunExp.selfTrainTest(X, y1, clfList, "MacroF1", testSize=0.2, prefix=prefix)
        else: # all-train-and-test  and leave-one-test
            prefix = "all, %s, %s, %s" % ('OLPDM+' + str(p['feature']), 
                    toStr(p['columnSource']), p['statementCol'])
            RunExp.allTrainTest(X, y1, topicMap, clfList, "MacroF1", testSize=0.2, prefix=prefix)
            RunExp.leaveOneTest(X, y1, topicMap, clfList, "MacroF1", prefix=prefix)


def runSingleTask(labelNewsList, taskType, olpdm, topicSet, sentiDict, params, clfList, topicMap=None, topicId=None):
    # generate word features
    print('generating word features...', file=sys.stderr)
    p = params['tfidf']
    wm = WM.WordModel(labelNewsList, newsCols=p['columnSource'], 
                       statCol=p['statementCol'], feature=p['feature'])
    (X1, y1) = wm.genXY()
    volc1 = wm.getVolc()
    #print('Size of volc1:', len(volc1), file=sys.stderr)
    print('X1: (%d, %d)' % (X1.shape[0], X1.shape[1]), file=sys.stderr)
    
    # generate OLPDM features
    p = params['OLPDM']['model settings']
    allowedSeedWord = OLPDM.initAllowedSet(topicSet, p['seedWordType'])
    allowedFirstLayerWord = OLPDM.initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
    allowedRel = { t: None for t in topicSet }
    olpdm.setModel(allowedSeedWord, p['seedWordType']['type'], allowedFirstLayerWord, 
                p['firstLayerType']['type'], allowedRel)
    (X2, y2) = olpdm.genXY()
    volc2 = olpdm.getVolc()
    #print('Size of volc2:', len(volc2), file=sys.stderr)
    print('X2: (%d, %d)' % (X2.shape[0], X2.shape[1]), file=sys.stderr)
    
    for i, y in enumerate(y1):
        assert y == y2[i]

    # merge (horozontally align) two matrix
    X = DataTool.hstack(X1, X2)
    volc3 = mergeVolc(volc1, volc2)
    #print('Size of merged volc:', len(volc3), file=sys.stderr)
    print('X: %d %d' % (X.shape[0], X.shape[1]), file=sys.stderr)

    # run #TODO: feature meaning 
    if taskType == 'SelfTrainTest':
        prefix = "%s, %s, %s, %s, %s" % (topicId, toStr(list(params.keys())), toStr(params), '"None"', 'False')
        rs = RunExp.selfTrainTest(X, y1, clfList, 'MacroF1', testSize=0.2, prefix=prefix)
        for r in rs:
            r['volc'] = volc3
            r['params'] = params

    elif taskType == 'AllTrainTest': 
        prefix = "%s, %s, %s, %s, %s" % ('all', toStr(list(params.keys())), toStr(params), '"None"', 'False')
        rs = RunExp.allTrainTest(X, y1, topicMap, clfList, 'MacroF1', testSize=0.2, prefix=prefix)
        for r in rs:
            r['volc'] = volc3
            r['params'] = params

    elif taskType == 'LeaveOneTest':
        prefix = "%s, %s, %s, %s, %s" % (topicId, toStr(list(params.keys())), toStr(params), '"None"', 'False')
        rs = RunExp.leaveOneTest(X, y1, topicMap, clfList, "MacroF1", testTopic=[topicId], prefix=prefix)
        for r in rs[topicId]:
            r['volc'] = volc3
            r['params'] = params

            
    return rs

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print('Usage:', sys.argv[0], 'SegAndDepLabelNewsJson phraseJson sentiDict WMParamsJson OLPDMParamsJson', file=sys.stderr)
        exit(-1)
    
    # arguments
    labelNewsJson = sys.argv[1]
    phraseJson = sys.argv[2]
    sentiDictFile = sys.argv[3]
    WMParamsJson = sys.argv[4]
    OLPDMParamsJson = sys.argv[5]

    # load labels and news 
    with open(labelNewsJson, 'r') as f:
        labelNewsList = json.load(f)
    
    # ====== initialization ======
    # load phrases
    topicPhraseList = loadPhraseFile(phraseJson)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    # get the set of all possible topic
    topicSet = set([labelNews['statement_id'] for labelNews in labelNewsList])
    # contruct in the process of constructing phrase dependency tree
    allowedFirstLayerWord = { topicId: set(sentiDict.keys()) for topicId in topicSet }
    allowedRel = { topicId: None for topicId in topicSet }
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]

    # ====== initalizing parameters ======
    clfList = ['NaiveBayes', 'MaxEnt']
    # print result of first Line
    ResultPrinter.printFirstLine()

    # ==================================================================== #
    # Run experiments on given list of parameters                          #
    # ==================================================================== #

    # read best parameters of two model
    WMParams = Parameter.loadFrameworkTopicParams(WMParamsJson)
    OLPDMParams = Parameter.loadFrameworkTopicParams(OLPDMParamsJson)
    
    # ============= Run for self-train-test ===============
    print('Self-Train-Test...', file=sys.stderr)
    labelNewsInTopic = dataTool.divideLabel(labelNewsList)
    for t in topicSet:
        bestR = None
        olpdm = OLPDM.OneLayerPhraseDepModel(labelNewsInTopic[t], topicPhraseList)
        paramsIter = Parameter.getParamsIter(WMParams['SelfTrainTest'][t], 'tfidf',
                OLPDMParams['SelfTrainTest'][t], 'OLPDM')
        for p in paramsIter:
            r = runSingleTask(labelNewsInTopic[t], 'SelfTrainTest', olpdm, topicSet, 
                    sentiDict, p, clfList, topicId=t)
            bestR = keepBestResult(bestR, r, 'MacroF1')
        #print(bestR)
        with open('SelfTrainTest_topic%d.pickle' % t, 'w+b') as f:
            pickle.dump(bestR, f)
    

    olpdm = OLPDM.OneLayerPhraseDepModel(labelNewsList, topicPhraseList)
    
    # ============= Run for all-train-test ================
    print('All-Train-Test...', file=sys.stderr)
    paramsIter = Parameter.getParamsIter(WMParams['AllTrainTest'], 'tfidf', 
            OLPDMParams['AllTrainTest'], 'OLPDM')
    bestR = None
    for p in paramsIter:
        r = runSingleTask(labelNewsList, 'AllTrainTest', olpdm, topicSet, sentiDict, 
                p, clfList, topicMap=topicMap)
        bestR = keepBestResult(bestR, r, 'MacroF1')
    #print(bestR)
    with open('AllTrainTest.pickle', 'w+b') as f:
        pickle.dump(bestR, f)
    
    # ============= Run for leave-one-test ================
    print('Leave-One-Test...', file=sys.stderr)
    for t in topicSet:
        bestR = None
        paramsIter = Parameter.getParamsIter(WMParams['LeaveOneTest'][t], 'tfidf', 
            OLPDMParams['LeaveOneTest'][t], 'OLPDM')
        for p in paramsIter:
            r = runSingleTask(labelNewsList, 'LeaveOneTest', olpdm, topicSet, sentiDict, 
                p, clfList, topicMap=topicMap, topicId=t)
            bestR = keepBestResult(bestR, r[t], 'MacroF1')
        #print(bestR)
        with open('LeaveOneTest_topic%d.pickle' % t, 'w+b') as f:
            pickle.dump(bestR, f)

    '''
    # run all combination
    params = { 'feature': ['0/1', 'tf', 'tfidf'],
                'column': [['content'], ['title'], ['title', 'content']],
                'statement': [False, True],
                'seedWordPOSType': [('NP',), ('NP', 'NR'), ('NP', 'NN', 'NR')]
            }
    paramsIter = ParameterGrid(params)
       

    mainProcedure(labelNewsList, paramsIter, clfList, allowedFirstLayerWord, 
        allowedRel, topicMap=topicMap, topicId=None)

    topicLabelNewsList = dataTool.divideLabel(labelNewsList)
    for topicId, labelNewsList in topicLabelNewsList.items():
        mainProcedure(labelNewsList, paramsIter, clfList, allowedFirstLayerWord, 
        allowedRel, topicMap=None, topicId=topicId)
    '''

    '''
    oldms = dict()
    # all topic are mixed to train and predict/ leave-one-test
    for p in paramsIter:
        # generate tfidf features
        print('generating tfidf features...', file=sys.stderr)
        (X1, y1) = tfidf.generateXY(labelNewsList, newsCols=p['column'], 
                       statementCol=p['statement'], feature=p['feature'])
        print('X1: (%d, %d)' % (X1.shape[0], X1.shape[1]), file=sys.stderr)

        # generate OLPDM features
        print('generating OLPDM features...', file=sys.stderr)

        # saving model for speed up
        if p['seedWordPOSType'] not in oldms:
            allowedSeedWord = { topicId: set(p['seedWordPOSType']) for topicId in topicSet }
            print(allowedSeedWord)
            oldm = OLPDM.OneLayerPhraseDepModel(labelNewsList, topicPhraseList, allowedSeedWord, 
                'tag', allowedFirstLayerWord, 'word', allowedRel)
            oldms[p['seedWordPOSType']] = oldm
        else:
            oldm = oldms[p['seedWordPOSType']]

        (X2, y2) = oldm.genXY()
        print('X2: (%d, %d)' % (X2.shape[0], X2.shape[1]), file=sys.stderr)

        # merge (horozontally align) two matrix
        X = DataTool.hstack(X1, X2)
        print('X: %d %d' % (X.shape[0], X.shape[1]), file=sys.stderr)
        
        # all train and test
        prefix = "all, %s, %s, %s" % ('OLPDM+' + str(p['feature']), list2Str(p['column']), p['statement'])
        RunExp.allTrainTest(X, y1, topicMap, clfList, "MacroF1", testSize=0.2, prefix=prefix)
        # leave one test
        RunExp.leaveOneTest(X, y1, topicMap, clfList, "MacroF1", prefix=prefix)
    '''

