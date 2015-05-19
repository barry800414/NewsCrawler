#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.grid_search import ParameterGrid

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
    # depParsedLabelNews: The list of parsed label-news
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

    def __init__(self, depParsedLabelNews, topicPhraseList, wVolc=None):
        self.topicPhraseList = topicPhraseList
        super(OneLayerPhraseDepModel, self).__init__(depParsedLabelNews, wVolc=wVolc)

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


def genXY(olpdm, params, topicSet, sentiDict):
    print('generating one layer dependency features...', file=sys.stderr)
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


def initOLDM(labelNewsList, topicPhraseList=None, wVolc=None):
    if topicPhraseList != None: #OLPDM
        olpdm = OneLayerPhraseDepModel(labelNewsList, topicPhraseList, 
                wVolc=wVolc)
    else: #OLDM (no phrase)
        olpdm = OneLayerDepModel(labelNewsList, wVolc=wVolc)
    return olpdm

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:', sys.argv[0], 'DepParsedLabelNewsJson ModelConfig SentiDictFile [-p phraseFile] [-v volcFile]', file=sys.stderr)
        exit(-1)

    depParsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    sentiDictFile = sys.argv[2]
    modelConfigFile = sys.argv[3]

    # load dependency parsed label news
    with open(depParsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    
    # load model configs 
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)

    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)

    # load other files
    topicPhraseList = None
    wVolc = None
    wVolcPrefix = ''
    for i in range(4, len(sys.argv)):
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

    # model parameters #FIXME: allowed relation
    randSeedList = config['setting']['randSeedList']
    paramsIter = ParameterGrid(config['params'])
    clfList = config['setting']['clfList']
    modelName = config['setting']['modelName']
    dataset = config['setting']['dataset']

    # get the set of all possible topic
    topicSet = set([ln['statement_id'] for ln in labelNewsList])
    topicMap = [ labelNewsList[i]['statement_id'] for i in range(0, len(labelNewsList)) ]
    labelNewsInTopic = divideLabel(labelNewsList)

    ResultPrinter.printFirstLine()

    # intialize the model
    print('Intializing the model...', file=sys.stderr)
    olpdm = initOLDM(labelNewsList, topicPhraseList, wVolc)
    tolpdm = { t: OLDM.initOLDM(ln, topicPhraseList, wVolc) for t, ln in labelNewsInTopic.items() }
 
    # ============= Run for self-train-test ===============
    print('Self-Train-Test...', file=sys.stderr)
    for t in topicSet:
        bestR = None
        for p in paramsIter:
            (X, y, volc) = genXY(tolpdm[t], p, topicSet, sentiDict)
            rsList = RunExp.runTask(X, y, volc, 'SelfTrainTest', 
                    p, clfList, topicId=t, randSeedList=randSeedList)
            bestR = keepBestResult(bestR, rsList, targetScore)
        with open('%s_%s_%s_SelfTrainTest_topic%d.pickle' % (modelName, dataset, wVolcPrefix, t), 'w+b') as f:
            pickle.dump(bestR, f)

    # ============= Run for all-train-test & leave-one-test ================
    print('All-Train-Test & Leave-One-Test...', file=sys.stderr)
    bestR = None # for all-train-test
    bestR2 = {t:None for t in topicSet}  # for leave-one-test

    for p in paramsIter:
        (X, y, volc) = genXY(olpdm, p, topicSet, sentiDict)
        rsList = RunExp.runTask(X, y, volc, 'AllTrainTest', p, clfList, topicMap=topicMap, 
                randSeedList=randSeedList)
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
