#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix

import dataTool
from OneLayerDepModel import *
from PhraseDepTree import *
from sentiDictSum import readSentiDict
from RunExperiments import *

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

    def __init__(self, parsedLabelNews, topicPhraseList, allowedSeedWord, 
            allowedSeedWordType, allowedFirstLayerWord, allowedFirstLayerWordType, 
            allowedRel):
        super(OneLayerPhraseDepModel, self).__init__(parsedLabelNews, 
                allowedSeedWord, allowedSeedWordType, allowedFirstLayerWord, 
                allowedFirstLayerWordType, allowedRel)
        self.topicPhraseList = topicPhraseList

    # override
    def getDepTree(self, tdList, topicId):
        pdt = PhraseDepTree(tdList, self.topicPhraseList[topicId])
        if pdt.isValid():
            pdt.construct()
            return pdt
        return None


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

    # model setting
    seedWordPOSType = ['NP'] #FIXME: how about NN, NR?
    #firstLayerPOSType = ['VA', 'VV', 'JJ', 'AD']
    #thresList = [0.01, 0.005, 0.001, 0.0005, 0.00001]

    clfList = ['NaiveBayes', 'MaxEnt', 'SVM' ]

    # here we don't have to specify allowed phrases words, because only valid phrases are 
    # contruct in the process of constructing phrase dependency tree
    allowedSeedWord = { topicId: set(seedWordPOSType) for topicId in topicSet }
    allowedFirstLayerWord = { topicId: set(sentiDict.keys()) for topicId in topicSet }
    allowedRel = { topicId: None for topicId in topicSet }
    
    topicMap = [ parsedLabelNews[i]['statement_id'] for i in range(0, len(parsedLabelNews)) ]
    # all news are mixed to train and test
    oldm = OneLayerPhraseDepModel(parsedLabelNews, topicPhraseList, allowedSeedWord,
                'tag', allowedFirstLayerWord, 'word', allowedRel)
    (X, y) = oldm.genXY()
    
    prefix = "%s, %s, %s, %s" % ('all', 'OneLayerPhraseDep', '[content]', 'False')
    RunExp.allTrainTest(X, y, topicMap, clfList, 'MacroF1', testSize=0.2, prefix=prefix)
    RunExp.leaveOneTest(X, y, topicMap, clfList, "MacroF1", prefix=prefix)
    
    # news are divided into different topic to train and test
    labelNewsInTopic = dataTool.divideLabel(parsedLabelNews)
    for topicId, labelNewsList in labelNewsInTopic.items():
        print('topicId:', topicId, file=sys.stderr)
        # building the model
        oldm = OneLayerPhraseDepModel(labelNewsList, topicPhraseList, allowedSeedWord,
                'tag', allowedFirstLayerWord, 'word', allowedRel)
        (X, y) = oldm.genXY()
        
        prefix = "%d, %s, %s, %s" % (topicId, 'OneLayerPhraseDep', '[content]', 'False')
        RunExp.selfTrainTest(X, y, clfList, 'MacroF1', testSize=0.2, prefix=prefix)

            
    
