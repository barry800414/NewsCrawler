#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import numpy as np
from scipy.sparse import csr_matrix

import dataTool
from OneLayerDepModel import *
from PhraseDepTree import *

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
        super(OneLayerPhraseDepModel, this).__init__(parsedLabelNews, 
                allowedSeedWord, allowedSeedWordType, allowedFirstLayerWord, 
                allowedFirstLayerWordType, allowedRel)
        self.topicPhraseList = topicPhraseList

    # override
    def getDepTree(self, tdList, topicId):
        return PhraseDepTree(tdList, self.topicPhraseList[topicId])


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
    sentiDict = SentiDictSum.readSentiDict(sentiDictFile)

    # get the set of all possible topic
    topicSet = set()
    for labelNews in parsedLabelNews:
        topicSet.add(labelNews['statement_id'])

    # model setting
    seedWordPOSType = ['NP'] #FIXME: how about NN, NR?
    #firstLayerPOSType = ['VA', 'VV', 'JJ', 'AD']
    #thresList = [0.01, 0.005, 0.001, 0.0005, 0.00001]

    '''
    # all news are mixed to train and test
    for threshold in thresList:
        allowedSeedWord = dict() 
        allowedFirstLayerWord = dict()
        allowedRel = dict()
        for topicId in topicSet:
            allowedSeedWord[topicId] = WFMapping.getAllowedWords(WFDict[topicId], seedWordPOSType, threshold)
            allowedFirstLayerWord[topicId] = WFMapping.getAllowedWords(WFDict[topicId], firstLayerPOSType, threshold)
            allowedRel[topicId] = None
            
            for pos in seedWordPOSType:
                print('#%s:%d' % (pos, len(allowedSeedWord[topicId][pos])), end='\t')
            for pos in firstLayerPOSType:    
                print('#%s:%d' % (pos, len(allowedFirstLayerWord[topicId][pos])), end='\t')
            print('')

        # building the model
        oldm = OneLayerDepModel(parsedLabelNews, allowedSeedWord, 
            allowedFirstLayerWord, allowedRel)
        (X, y) = oldm.genXY()
    
        MLProcedure.runExperiments(X, y, clfList=['NaiveBayes', 'SVM'], 
            prefix='Threshold=%f' % (threshold))
    '''
    # news are divided into different topic to train and test
    labelNewsInTopic = dataTool.divideLabel(parsedLabelNews)
    for topicId, labelNewsList in labelNewsInTopic.items():
        # here we don't have to specify allowed phrases words, because only valid phrases are 
        # contruct in the process of constructing phrase dependency tree
        allowedSeedWord = { topicId: set(seedWordPOSType) } 
        allowedFirstLayerWord = set(sentiDict.keys())
        allowedRel[topicId] = None
                
        # building the model
        oldm = OneLayerPhraseDepModel(labelNewsList, topicPhraseList, allowedSeedWord,
                'tag', allowedFirstLayerWord, 'word', allowedRel)
        (X, y) = oldm.genXY()
        
            #MLProcedure.runExperiments(X, y, clfList=['NaiveBayes', 'MaxEnt',  'SVM'], 
            #    prefix='topicId=%d, Threshold=%f' % (topicId,threshold))

    
