#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.grid_search import ParameterGrid

#import WordModel as WM
#import OneLayerDepModel as OLDM
#import OpinionModel as OM
import TreePattern as TP
import NegPattern as NP
from PhraseDepTree import loadPhraseFile
from RunExperiments import *
from Volc import Volc
from misc import *
import Parameter

'''
Author: Wei-Ming Chen
Date: 2015/06/06
'''

# merge features
def mergeXY(X_y_volc_Dict):
    mX = None
    my = None
    mVolc = None
    mWVolc = None
    for key, (X, y, volc, wVolc) in X_y_volc_Dict.items():  
        print('%s: X:(%d, %d)' % (key, X.shape[0], X.shape[1]), file=sys.stderr)
        mX = X if mX is None else DataTool.hstack(mX, X)
        if my is not None:
            assert np.array_equal(my, y)
        else:
            my = y
        mVolc = volc if mVolc is None else Volc.mergeVolc(mVolc, volc)
        mWVolc = wVolc if mWVolc is None else Volc.mergeVolc(mWVolc, wVolc)

    print('Final: X:(%d, %d)' % (mX.shape[0], mX.shape[1]), file=sys.stderr)
    return (mX, my, mVolc, wVolc)

# modelPickle[m][t]: is the pickle of model m in topic t (including 'all')
def getMergedXY(modelPickle, topic):
    mX = None
    my = None
    volcDictList = list()
    for modelName, pickleDict in modelPickle.items():
        pickleObj = pickleDict[topic]
        #print(pickleObj.keys())
        X = pickleObj['data']['X']
        y = pickleObj['data']['y']
        volcDict = pickleObj['volcDict']
        print(modelName, X.shape, sep=':', file=sys.stderr)
        mX = X if mX is None else DataTool.hstack(mX, X)
        if my is not None: assert np.array_equal(my, y)
        else: my = y     
        volcDictList.append(volcDict)
    print('Final:', mX.shape, file=sys.stderr)
    return (mX, my, volcDictList)

def loadPickleFiles(pickleFilePrefix, topicSet):
    pickleDict = dict()
    for t in topicSet:
        if type(t) == str and t == 'all':
            with open(pickleFilePrefix + '_AllTrainTest.pickle', 'r+b') as f:
                pickleDict['all'] = pickle.load(f)
        else:
            with open(pickleFilePrefix + '_SelfTrainTest_topic%d.pickle' % t, 'r+b') as f:
                pickleDict[t] = pickle.load(f)
    return pickleDict

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:', sys.argv[0], 'LabelNewsJsonFile MergedModelConfig [[-name PickleFilePrefix] ...]  ', file=sys.stderr)
        exit(-1)
    
    # read in arguments
    labelNewsJsonFile = sys.argv[1] # FIXME: to retrieve topicMap
    modelConfigFile = sys.argv[2]

    # load model config
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)

    toRun = config['toRun']
    taskName = config['taskName']
    setting = config['setting']
    targetScore = config['setting']['targetScore'] 

    # load labels and news 
    with open(labelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    topicSet = set([labelNews['statement_id'] for labelNews in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)
    newsIdList = { t:[ln['news_id'] for ln in labelNewsInTopic[t]] for t in topicSet }
    newsIdList['All'] = [ln['news_id'] for ln in labelNewsList] 

    toLoadTopicList = list()
    if 'SelfTrainTest' in toRun:
        toLoadTopicList.extend(list(topicSet))
    if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
        toLoadTopicList.append('all')

    modelPickle = dict()
    for i in range(3, len(sys.argv)):
        if sys.argv[i][0] == '-' and len(sys.argv) > i:
            name = sys.argv[i][1:]
            modelPickle[name] = loadPickleFiles(sys.argv[i+1], toLoadTopicList)
    
    print(modelPickle.keys(), file=sys.stderr)
    assert len(modelPickle) >= 2 # at least two model
    
    # print result of first Line
    ResultPrinter.printFirstLine()
                
    # ============= Run for self-train-test ===============
    if 'SelfTrainTest' in toRun:
        print('Self-Train-Test...', file=sys.stderr)
        for t in topicSet:
            bestR = None
            (X, y, volcDictList) = getMergedXY(modelPickle, t)
            expLog = RunExp.runTask(X, y, volcDictList, newsIdList[t], 'SelfTrainTest', None, topicId=t, **setting)
            with open('%s_SelfTrainTest_topic%d.pickle' % (taskName, t), 'w+b') as f:
                pickle.dump(expLog, f)
    
    # ============= Run for all-train-test ================
    if 'AllTrainTest' in toRun or 'LeaveOneTest' in toRun:
        (X, y, volcDictList) = getMergedXY(modelPickle, 'all')
    if 'AllTrainTest' in toRun:
        print('All-Train-Test ...', file=sys.stderr)
        expLog = RunExp.runTask(X, y, volcDictList, newsIdList['All'], 'AllTrainTest', None, topicMap=topicMap, **setting)
        with open('%s_AllTrainTest.pickle' %(taskName), 'w+b') as f:
            pickle.dump(expLog, f)
    
    # ============ Leave-One-Test ===============
    if 'LeaveOneTest' in toRun:
        for t in topicSet:
            expLog = RunExp.runTask(X, y, volcDictList, newsIdList['All'], 'LeaveOneTest', None, topicMap=topicMap, topicId=t, **setting)
            with open('%s_LeaveOneTest_topic%d.pickle' %(taskName, t), 'w+b') as f:
                pickle.dump(expLog, f)

