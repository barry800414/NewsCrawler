#!/usr/bin/env python3

import sys
import json
import WFDict
from DepGraph import DepGraph

'''
This codes implements the OneLayerDepModel for stance classification.
DepGraph.py, WFDict.py and Word->frequency mapping are required.
Author: Wei-Ming Chen
Date: 2015/03/08
Last Updated: 2015/03/08
'''

class OneLayerDepModel():
    # parsedLabelNews: The list of parsed label-news
    # allowedSeedWord[T][P]: a set of allowed words with `P` POS-Tag in topic T 
    # allowedFirstLayer[T][P]
    # allowedRel[T][P]
    def __init__(self, parsedLabelNews, allowedSeedWord, 
            allowedFirstLayerWord, allowedRel):
        self.pln = parsedLabelNews
        self.asw = allowedSeedWord
        self.aflw = allowedFirstLayerWord
        self.ar = allowedRel
        self.seedVolc = dict() # seed word volcabulary
        self.__initSeddVolc()  
        self.newVolc = dict() # word volcabulary for first layer
        
    # TODO: word/word-tag/word-relation??
    # initialize the seed word volcabulary
    def __initSeedVolc(self):
        for topicId, seedWord in self.asw.items():
            for tag, wordSet in seedWord.items():
                addWordSetToVolc(self.seedVolc)
        print('#seedVolc:', len(self.seedVolc), file=sys.stderr)

    # generate X, y 
    def genXY(self):
        for labelNews in parsedLabelNews:
            topicId = labelNews['statement_id'] # FIXME
            contentDep = labelNews['news']['content_dep'] #TODO: title, content, statement
            for depList in contentDep:
                # generate dependency graph for each dependency list
                dg = DepGraph(depList, 1)
                dg.setAllowedDepWord(allowedFirstLayerWord[topicId], type='[t][w]')
                dg.setAllowedGovWord(allowedFirstLayerWord[topicId], type='[t][w]')
                dg.setAllowedRel(allowedRel[topicId])
                dg.setNowWord(allowedSeedWord[topicId])
                
                # go one step for searching dependencies (edges) which matches the rule
                edgeList = dg.searchOneStep()
                
                # add new word to volcabulary
                newWordSet = set([eW for rel,sP,sW,sT,eP,eW,eT in edgeList])
                addWordSetToVolc(newWordSet, self.newVolc)

                # save all the searched depenencies for later usage
                newsEdgeList.append(edgeList)

            # corpusEdgeList[newsIndex][depGraphIndex][edgeIndex]
            corpusEdgeList.append(newsEdgeList)

        print("#newVolc:", len(self.newVolc))

        # converting all extraced dependencies to features X
        # Here the features are the word counts from each seed word, 
        # so the dimension of X will be len(seedVolc) * len(newVolc)
        base = len(seedVolc)
        XFeature = [defaultdict(int) for i in range(0, len(parsedLabelNews))]
        for i, newsEdgeList in enumerate(corpusEdgeList):
            for edgeList in newsEdgeList:
                for rel,sP,sW,sT,eP,eW,eT in edgeList:
                    index = seedVolc[sW] * base + newVolc[eW]
                    XFreature[i][index] += 1
        
        rows = list()
        cols = list()
        entries = list()
        for rowId, cntDict in enumerate(XFeature):
            for colId, cnt in cntDict.items():
                rows.append(rowId)
                cols.append(colId)
                entries.append(cnt)
        X = csr_matrix(entries, (rows, cols), dtype=np.float64)
        y = np.array(getLabels(parsedLabelNews))

        return (X, y)


# get labels from the list of label-news
def getLabels(labelNewsList):
    mapping = { "neutral" : 1, "oppose": 0, "agree" : 2 } 
    labelList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in mapping:
            labelList.append(mapping[labelNews['label']])
    return labelList


# add a set of word to volcabulary
def addWordSetToVolc(wordSet, volc):
    for w in wordSet:
        if w not in volc:
            volc[w] = len(volc)

'''
# list of parsedLabelNews: label & news 
# allowedWTList: allowed words for each kind of tag in each layer
#    allowedWTList[0]['NN']: the words allowed of NN in 0 layer (seed)
# allowedRelList: allowed dependency relations in each layer
def generateXYOneLayer(parsedLabelNews, allowedSeedWord, 
        allowedFirstLayerWord, allowedRel):
    
    Y = list()
    XFeature = list()
    volc = dict()
    
    # convert to X 
    # TODO:word/word-tag/word-relation ?
    seedVolc = dict()
    newVolc = dict()
    for contentEdgeList in corpusEdgeList:
        for depGraphEdgeList in contentEdgeList:
            for edge in depGraphEdgeList:
                
   

# list of parsedLabelNews: label & news 
# allowedWTList: allowed words for each kind of tag in each layer
#    allowedWTList[0]['NN']: the words allowed of NN in 0 layer (seed)
# allowedRelList: allowed dependency relations in each layer
def generateXY(parsedLabelNews, allowedWTList, allowedRelList):
    # check input
    #if len(allowedWTList) != (len(allowedRelList)+1) :
        #return None

    maxLayer = len(allowedWTList) - 1
    Y = list()
    XFeature = list()
    volc = dict()
    for labelNews in parsedLabelNews:
        contentDep = resetDep(labelNews['news']['content_dep'])
        allEdgeList = list() #
        for depList in contentDep:
            dg = DepGraph(depList, maxLayer)
            edgeListLayer = list() #edgeListLayer[layer][edgeIndex]
            edgeList = None
            for layer in range(0, maxLayer):
                dg.setAllowedDepWord(allowedWTList[layer+1], type='[t][w]')
                dg.setAllowedGovWord(allowedWTList[layer+1], type='[t][w]')
                dg.setAllowedRel(allowedRelList[layer])
                if layer == 0:
                    dg.setNowWord(allowedWTList[0])
                else:
                    if edgeList != None:
                        nowWords = [eP for rel,sP,sW,sT,eP,eW,wT in edgeList]
                        dg.setNowWord(nowWords, type='pos')
                edgeList = dg.searchOneStep()
                edgeListLayer.append(edgeList)
            allEdgeList.append(edgeListLayer)
'''

# TODO: calculate frequency from dependencies

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'parsedLabelNewsJson', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1]

    # load label-news
    with open(parsedLabelNewsJsonFile, 'r') as f:
        parsedLabelNewsJson = json.load(f)

    # model setting
    seedWordPOSType = ['NN', 'NR'] 
    firstLayerPOSType = ['VA', 'VV', 'JJ', 'AD']
    WF_FOLDER = './'

    # loading word-frequency mapping from file
    seedWFDict = dict() # seedWFDict[StatId][pos] => a word->frequency mapping
    for type in seedWordPOSType:
        allowedSeedWord[type] = WFDict.loadWFDict(WF_FOLDER + '%s_WFMapping.json' % (type))

    firstLayerWFDict = dict()
    for type in firstLayerPOSType:
        allowedFirstLayerWord[type] = WFDict.loadWFDict(WF_FOLDER + '%s_WFMapping.json' % (type))

    # for each threshold, filter out some words
    for threshold in [0.5]:
        allowedSeedWord = dict() 
        allowedFirstLayerWord = dict()
        allowedRel = dict()
        for topicId in [2, 3, 4, 5, 6, 10, 13, 16]:
            allowedSeedWord[topicId] = filteredByThreshold(seedWFDict[topicId], threshold)
            allowedFirstLayerWord[topicId] = filteredByThreshold(firstLayerWFDict[topicId], threshold)    
            allowedRel[topicId] = None

        # building the model
        oldm = OneLayerDepModel(parsedLabelNews, allowedSeedWord, 
            allowedFirstLayerWord, allowedRel)
        (X, y) = oldm.genXY()
        
        # training and validation

        # testing 

        # evaluation 

        # print out results


