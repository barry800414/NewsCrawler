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

    def __init__(self, parsedLabelNews, topicPhraseList):
        self.topicPhraseList = topicPhraseList
        super(OneLayerPhraseDepModel, self).__init__(parsedLabelNews)

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

# TODO: calculate frequency from dependencies
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'depParsedLabelNewsJson phraseFile sentiDictFile', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    phrasesJsonFile = sys.argv[2]
    sentiDictFile = sys.argv[3]

    # load label-news
    with open(parsedLabelNewsJsonFile, 'r') as f:
        parsedLabelNews = json.load(f)

    # load phrases
    topicPhraseList = loadPhraseFile(phrasesJsonFile)

    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)

    # get the set of all possible topic
    topicSet = set()
    for labelNews in parsedLabelNews:
        topicSet.add(labelNews['statement_id'])

    # model parameters #FIXME: allowed relation
    params = { 'seedWordType': [
                    {'type': 'tag', 'allow': ('NP',)},
                    {'type': 'tag', 'allow': ('NP','NR')},
                    {'type': 'tag', 'allow': ('NP','NR','NN')}
                ],
               'firstLayerType': [ 
                    {'type': 'word', 'allow': 'NTUSD_core'}, 
                    {'type': 'tag', 'allow': ('VV',)},
                    {'type': 'tag', 'allow': ('JJ',)},
                    {'type': 'tag', 'allow': ('VA',)},
                    {'type': 'tag', 'allow': ('VV','JJ')},
                    {'type': 'tag', 'allow': ('VV','VA')},
                    {'type': 'tag', 'allow': ('JJ','VA')},
                    {'type': 'tag', 'allow': ('VV','JJ','VA')} 
                ]
            }

    paramsGrid = ParameterGrid(params)
    clfList = ['NaiveBayes', 'MaxEnt', 'SVM' ]
    topicMap = [ parsedLabelNews[i]['statement_id'] for i in range(0, len(parsedLabelNews)) ]
    labelNewsInTopic = dataTool.divideLabel(parsedLabelNews)
    
    debugFolder = './debug'
    ResultPrinter.printFirstLine()

    # intialize the model
    print('Intializing the model...', file=sys.stderr)
    olpdm = OneLayerPhraseDepModel(parsedLabelNews, topicPhraseList)
    tolpdm = dict()
    for topicId, labelNewsList in labelNewsInTopic.items():
        tolpdm[topicId] = OneLayerPhraseDepModel(labelNewsList, 
                topicPhraseList)

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
        
