#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.grid_search import ParameterGrid

import dataTool
from OneLayerDepModel import *
from PhraseDepTree import *
from sentiDictSum import readSentiDict
from RunExperiments import *
from misc import *

'''
This codes implements the OneLayerPhraseDepModel for stance classification.
PhraseDepTree.py, DepTree.py, Phrases list, sentiment dictionary are required
Author: Wei-Ming Chen
Last Updated: 2015/04/11
'''

class OneLayerPhraseDepModel(OneLayerDepModel):
    # parsedLabelNews: The list of parsed label-news
    # topicPhraseList[T]: the list of phrase objects for constructing PhraseDepTree
    # if allowedSeedWordType = '[t][w]':
    #   allowedSeedWord[T][P]: a set of allowed words with `P` POS-Tag in topic T 
    # elif allowedSeedWordType = 'word':
    #   allowedSeedWord[T]: a set of allowed words (without considering POS tag)
    # elif allowedSeedWordType = 'tag':
    #   allowedSeedWord[T]: a set of allowe POS tag (without considering word)
    # 
    # allowedFirstLayerWord is similar to allowedSeedWord
    # allowedRel[T][P]

    def __init__(self, parsedLabelNews, topicPhraseList, wVolc=None):
        self.topicPhraseList = topicPhraseList
        super(OneLayerPhraseDepModel, self).__init__(parsedLabelNews, wVolc=wVolc)

    # override
    def getDepTree(self, tdList, topicId):
        pdt = PhraseDepTree(tdList, self.topicPhraseList[topicId])
        if pdt.isValid():
            pdt.construct()
            return pdt
        return None

# initialize allowed set. dictionary: word -> score
def initAllowedSet(topicSet, config, dictionary=None):
    if config['type'] == 'word': #using words in dictionary
        allowedSet = { topicId: set(dictionary.keys()) for topicId in topicSet }
    elif config['type'] == 'tag': #using tag
        allowedSet = { topicId: set(config['allow']) for topicId in topicSet }
    return allowedSet


def genXY(olpdm, topicSet, sentiDict, params):
    p = params
    allowedSeedWord = initAllowedSet(topicSet, p['seedWordType'])
    allowedFirstLayerWord = initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
    allowedRel = { t: None for t in topicSet }
    olpdm.setModel(allowedSeedWord, p['seedWordType']['type'], 
            allowedFirstLayerWord, p['firstLayerType']['type'], 
            allowedRel, p['minCnt'])
    (X, y) = olpdm.genXY()
    volc = olpdm.getVolc()
    return (X, y, volc)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:', sys.argv[0], 'depParsedLabelNewsJson sentiDictFile [-p phraseFile] [-v volcFile]', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    sentiDictFile = sys.argv[2]

    # load label-news
    with open(parsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)

    
    topicPhraseList = None
    wVolc = None
    wVolcPrefix = ''
    for i in range(3, len(sys.argv)):
        if sys.argv[i] == '-p' and len(sys.argv) > i:
            # load phrase file
            phrasesJsonFile = sys.argv[i+1]
            topicPhraseList = loadPhraseFile(phrasesJsonFile)
            i = i + 1
        elif sys.argv[i] == '-v' and len(sys.argv) > i:
            # load word volcabulary file
            wordVolcFile = sys.argv[i+1]
            wVolcPrefix = getFileNamePrefix(wordVolcFile)
            wVolc = Volc()
            wVolc.load(wordVolcFile)
            wVolc.lock() # lock the volcabulary, all new words are viewed as OOV
            i = i + 1

    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])

    # model parameters #FIXME: allowed relation
    if topicPhraseList != None:
        params = { 'seedWordType': [
                    {'type': 'tag', 'allow': ('NP','NR','NN')}
                ],
               'firstLayerType': [ 
                    {'type': 'word', 'allow': 'NTUSD_core'}, 
                    {'type': 'tag', 'allow': ('VV','JJ','VA')} 
                ],
               'minCnt': [2]
            }
        modelName = 'OLPDM'
    else:
        params = { 'seedWordType': [
                    {'type': 'tag', 'allow': ('NR','NN')}
                ],
               'firstLayerType': [ 
                    {'type': 'word', 'allow': 'NTUSD_core'}, 
                    {'type': 'tag', 'allow': ('VV','JJ','VA')} 
                ],
                'minCnt': [2]
            }
        modelName = 'OLDM'
    
    randSeedList = [1, 2, 3, 4, 5]
    paramsIter = ParameterGrid(params)
    clfList = ['NaiveBayes', 'MaxEnt', 'SVM' ]
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = dataTool.divideLabel(labelNewsList)
    
    debugFolder = './debug'
    ResultPrinter.printFirstLine()

    # intialize the model
    print('Intializing the model...', file=sys.stderr)
    if topicPhraseList != None: #OLPDM
        olpdm = OneLayerPhraseDepModel(labelNewsList, topicPhraseList, 
                wVolc=wVolc)
        tolpdm = dict()
        for topicId, labelNewsList in labelNewsInTopic.items():
            #if topicId != 2:
            #    continue
            tolpdm[topicId] = OneLayerPhraseDepModel(labelNewsList, 
                    topicPhraseList, wVolc=wVolc) 
    else: #OLDM (no phrase)
        olpdm = OneLayerDepModel(labelNewsList, wVolc=wVolc)
        tolpdm = dict()
        for topicId, labelNewsList in labelNewsInTopic.items():
            #if topicId != 2:
            #    continue
            tolpdm[topicId] = OneLayerDepModel(labelNewsList, wVolc=wVolc)
 
    # ============= Run for self-train-test ===============
    print('Self-Train-Test...', file=sys.stderr)
    for t in topicSet:
        #if t != 2:
        #    continue
        bestR = None
        for p in paramsIter:
            (X, y, volc) = genXY(tolpdm[t], topicSet, sentiDict, p)
            rsList = RunExp.runTask(X, y, volc, 'SelfTrainTest', 
                    p, clfList, topicId=t, randSeedList=randSeedList)
            for rs in rsList:
                if rs != None:
                    bestR = keepBestResult(bestR, rs, 'MacroF1')
        with open('%s_%s_SelfTrainTest_topic%d.pickle' % (modelName, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)

    # ============= Run for all-train-test ================
    print('All-Train-Test...', file=sys.stderr)
    bestR = None
    for p in paramsIter:
        (X, y, volc) = genXY(olpdm, topicSet, sentiDict, p)
        rsList = RunExp.runTask(X, y, volc, 'AllTrainTest', p, clfList, topicMap=topicMap, 
                randSeedList=randSeedList)
        for rs in rsList:
            if rs != None:
                bestR = keepBestResult(bestR, rs, 'MacroF1')
    with open('%s_%s_AllTrainTest.pickle' %(modelName, wVolcPrefix), 'w+b') as f:
        pickle.dump(bestR, f)


    # ============= Run for leave-one-test ================
    print('Leave-One-Test...', file=sys.stderr)
    for t in topicSet:
        bestR = None
        for p in paramsIter:
            (X, y, volc) = genXY(olpdm, topicSet, sentiDict, p)
            rsList = RunExp.runTask(X, y, volc, 'LeaveOneTest', p, clfList, 
                    topicMap=topicMap, topicId=t, randSeedList=randSeedList)
            for rs in rsList:
                if rs != None:
                    bestR = keepBestResult(bestR, rs[t], 'MacroF1')
        with open('%s_%s_LeaveOneTest_topic%d.pickle' % (modelName, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)

    '''
    print('Experiments starts...', file=sys.stderr)
    for p in paramsGrid:
        print('Model Setting:', p, file=sys.stderr)
        print('All-Train-Test and Leave-One-Test ... ', file=sys.stderr)
        # initialization for this parameter
        allowedSeedWord = initAllowedSet(topicSet, p['seedWordType'])
        allowedFirstLayerWord = initAllowedSet(topicSet, p['firstLayerType'], sentiDict)
        allowedRel = { topicId: None for topicId in topicSet }

        ## allTrainTest and leaveOneTest
        fStr = 'allMixedPairs_%s_%s' %(toFStr(p['seedWordType']['allow']), 
                toFStr(p['firstLayerType']['allow']))
        debugFile = open(debugFolder + '/' + fStr+'.txt', 'w') 

        olpdm.setModel(allowedSeedWord, p['seedWordType']['type'], allowedFirstLayerWord, 
                p['firstLayerType']['type'], allowedRel, debugLevel=1, debugFile=debugFile)
        (X, y) = olpdm.genXY()
        prefix = "%s, %s, %s, %s, %s" % ('all', 'OneLayerPhraseDep', toStr(p), '["content"]', 'False')
        RunExp.allTrainTest(X, y, topicMap, clfList, 'MacroF1', testSize=0.2, prefix=prefix)
        RunExp.leaveOneTest(X, y, topicMap, clfList, "MacroF1", prefix=prefix)
        debugFile.close()
        
        ## selfTrainTest
        print('self-Train-Test ...', file=sys.stderr)
        for topicId in topicSet:
            print('topicId:', topicId, file=sys.stderr)
            fStr = 'topic%dPairs_%s_%s' %(topicId, toFStr(p['seedWordType']['allow']), 
                    toFStr(p['firstLayerType']['allow']))
            debugFile = open(debugFolder + '/' + fStr+'.txt', 'w') 
            tolpdm[topicId].setModel(allowedSeedWord, p['seedWordType']['type'], allowedFirstLayerWord, 
                p['firstLayerType']['type'], allowedRel, debugLevel=1, debugFile=debugFile)
            (X, y) = tolpdm[topicId].genXY()
            
            prefix = "%d, %s, %s, %s, %s" % (topicId, 'OneLayerPhraseDep', toStr(p),'["content"]', 'False')
            RunExp.selfTrainTest(X, y, clfList, 'MacroF1', testSize=0.2, prefix=prefix)
            debugFile.close()
        '''
