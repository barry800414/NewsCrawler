#!/usr/bin/env python3

import sys
import json
import math
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix, hstack
from sklearn.grid_search import ParameterGrid

import WordModelImproved as WM
import OneLayerPhraseDepModel as OLPDM
import OpinionModel as OM
import TreePattern as TP
import NegPattern as NP
from PhraseDepTree import loadPhraseFile
from sentiDictSum import readSentiDict
from RunExperiments import *
from Volc import Volc
from misc import *
import Parameter

'''
Author: Wei-Ming Chen
Date: 2015/05/19
'''

#TODO: merge OLDM & OLPDM, mergeVolc, 
def genXY(params, wm=None, oldm=None, om=None, labelNewsList=None, volc=None,
        topicSet=None, sentiDict=None, pTreeList=None, negPList=None):
    assert len(params) >= 2
    X_y_volc_Dict = dict()
    if 'WM' in params: 
        assert wm != None and labelNewsList != None
        X_y_volc_Dict['WM'] = WM.genXY(labelNewsList, wm, params['WM']['model settings'], volc)    
    if 'OLDM' in params: 
        assert oldm != None and topicSet != None and sentiDict != None
        X_y_volc_Dict['OLDM'] = OLPDM.genXY(oldm, params['OLDM']['model settings'], topicSet, sentiDict)
    if 'OM' in params:
        assert om != None and pTreeList != None and negPList != None
        X_y_volc_Dict['OM'] = OM.genXY(om, params['OM']['model settings'], pTreeList, negPList=negPList, sentiDict=sentiDict, wVolc=volc)
    
    (mX, my, mVolc) = mergeXY(X_y_volc_Dict)
    return (mX, my, mVolc)

# merge features
def mergeXY(X_y_volc_Dict):
    mX = None
    my = None
    mVolc = None
    for key, (X, y, volc) in X_y_volc_Dict.items():
        print('%s: X:(%d, %d)' % (key, X.shape[0], X.shape[1]), file=sys.stderr)
        mX = X if mX == None else DataTool.hstack(mX, X)
        if my != None:
            assert np.array_equal(my, y)
        else:
            my = y
        mVolc = volc if mVolc == None else Volc.mergeVolc(mVolc, volc)
    print('Final: X:(%d, %d)' % (mX.shape[0], mX.shape[1]), file=sys.stderr)
    return (mX, my, mVolc)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:', sys.argv[0], 'TagDepLabelNewsFile MergedModelConfig sentiDict [-options file]', file=sys.stderr)
        print('[-WM ParamJson] [-OLDM ParamJson] [-OM ParamJson] [-p PhraseFile] [-v VolcFile] ', file=sys.stderr)
        print('[-tp TreePatternFile] [-ng NegationPatternFile]', file=sys.stderr)
        exit(-1)
    
    # read in arguments
    labelNewsJson = sys.argv[1]
    modelConfigFile = sys.argv[2]
    sentiDictFile = sys.argv[3]
    modelNum = 0
    WMParamsJsonFile = None
    OLDMParamsJsonFile = None
    OMParamsJsonFile = None
    topicPhraseList = None
    pTreeList = None
    negPList = None
    wVolc = None
    wVolcPrefix = ''
    for i in range(4, len(sys.argv)):
        if sys.argv[i] == '-WM' and len(sys.argv) > i:
            WMParamsJsonFile = sys.argv[i+1]
            modelNum += 1
        elif sys.argv[i] == '-OLDM' and len(sys.argv) > i:
            OLDMParamsJsonFile = sys.argv[i+1]
            modelNum += 1
        elif sys.argv[i] == '-OM' and len(sys.argv) > i:
            OMParamsJsonFile = sys.argv[i+1]
            modelNum += 1
        elif sys.argv[i] == '-p' and len(sys.argv) > i:
            # load phrase file
            print('Loading topic phrase file ...', file=sys.stderr)
            topicPhraseList = loadPhraseFile(sys.argv[i+1])
        elif sys.argv[i] == '-v' and len(sys.argv) > i:
            # load word clustering vocabulary 
            print('Loading word volcabulary file ...', file=sys.stderr)
            wVolcPrefix = getFileNamePrefix(sys.argv[i+1])
            wVolc = Volc()
            wVolc.load(sys.argv[i+1])
            wVolc.lock() # lock the volcabulary, all new words are viewed as OOV
        elif sys.argv[i] == '-tp' and len(sys.argv) > i:
            # load pattern trees 
            pTreeList = TP.loadPatterns(sys.argv[i+1])
        elif sys.argv[i] == '-ng' and len(sys.argv) > i:
            # load negation pattern file
            negPList = NP.loadNegPatterns(sys.argv[i+1])
            
    assert modelNum >= 2 # at least two model
    
    # load labels and news 
    print('Loading labels and news ...', file=sys.stderr)
    with open(labelNewsJson, 'r') as f:
        labelNewsList = json.load(f)  
    # load model config
    print('Reading merged model config ...', file=sys.stderr)
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)
    targetScore = config['setting']['targetScore']
    randSeedList = config['setting']['randSeedList']
    clfList = config['setting']['clfList']
    modelName = config['setting']['modelName']
    dataset = config['setting']['dataset']

    topicSet = set([labelNews['statement_id'] for labelNews in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]

    # initialize models
    allParams = dict()
    wm = None
    oldm = None
    toldm = {t:None for t in topicSet}
    om = None 
    tom = {t:None for t in topicSet}
    labelNewsInTopic = divideLabel(labelNewsList)
    if WMParamsJsonFile != None:
        print('initializing WordModel ...', file=sys.stderr)
        allParams['WM'] = Parameter.loadFrameworkTopicParams(WMParamsJsonFile)
        wm = WM.initWM()
    if OLDMParamsJsonFile != None:
        print('intializing OLDM ...', file=sys.stderr)
        allParams['OLDM'] = Parameter.loadFrameworkTopicParams(OLDMParamsJsonFile)
        oldm = OLPDM.initOLDM(labelNewsList, topicPhraseList, wVolc)
        toldm = { t: OLPDM.initOLDM(ln, topicPhraseList, wVolc) for t, ln in labelNewsInTopic.items() }
    if OMParamsJsonFile != None:
        print('initializing OM ...', file=sys.stderr)
        allParams['OM'] = Parameter.loadFrameworkTopicParams(OMParamsJsonFile)
        om = OM.initOM(labelNewsList, topicPhraseList)
        tom = { t: OM.initOM(ln, topicPhraseList) for t, ln in labelNewsInTopic.items() }
    
    # print result of first Line
    ResultPrinter.printFirstLine()

    # ============= Run for self-train-test ===============
    
    print('Self-Train-Test...', file=sys.stderr)
    for t in topicSet:
        bestR = None
        paramsIter = Parameter.getParamsIter(allParams, framework='SelfTrainTest', topicId=t)
        for p in paramsIter:
            (X, y, volc) = genXY(p, wm, toldm[t], tom[t], 
                    labelNewsInTopic[t], wVolc, topicSet, 
                    sentiDict, pTreeList, negPList)
            rsList = RunExp.runTask(X, y, volc, 'SelfTrainTest', 
                    p, clfList, topicId=t, randSeedList=randSeedList)
            bestR = keepBestResult(bestR, rsList, targetScore)
        with open('%s_%s_%s_SelfTrainTest_topic%d.pickle' % (modelName, 
            dataset, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)
    
    # ============= Run for all-train-test ================
    
    print('All-Train-Test ...', file=sys.stderr)
    bestR = None # for all-train-test
    
    paramsIter = Parameter.getParamsIter(allParams, framework='AllTrainTest')
    for p in paramsIter:
        (X, y, volc) = genXY(p, wm, oldm, om, labelNewsList, 
                wVolc, topicSet, sentiDict, pTreeList, negPList)

        rsList = RunExp.runTask(X, y, volc, 'AllTrainTest', p, 
                clfList, topicMap=topicMap, randSeedList=randSeedList)
        bestR = keepBestResult(bestR, rsList, targetScore)
    with open('%s_%s_%s_AllTrainTest.pickle' %(modelName, dataset, wVolcPrefix), 'w+b') as f:
        pickle.dump(bestR, f)
    
    
    # ============ Leave-One-Test ===============
    for t in topicSet:
        bestR = None
        paramsIter = Parameter.getParamsIter(allParams, framework='LeaveOneTest', topicId=t)
        for p in paramsIter:
            (X, y, volc) = genXY(p, wm, oldm, om, labelNewsList, wVolc, 
                    topicSet, sentiDict, pTreeList, negPList)

            rsList = RunExp.runTask(X, y, volc, 'LeaveOneTest', p, clfList, 
                    topicMap=topicMap, topicId=t, randSeedList=randSeedList)
            bestR = keepBestResult(bestR, rsList, targetScore, topicId=t)
        with open('%s_%s_%s_LeaveOneTest_topic%d.pickle' %(
            modelName, dataset, wVolcPrefix, t), 'w+b') as f:
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

