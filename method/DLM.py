#!/usr/bin/env python3 

import sys
import json
from collections import defaultdict

'''
This code implements the DLM model
Date: 2015/03/06
Author: Wei-Ming Chen
'''

WF_Folder = './'

# load word-frequency mapping for each statement
def loadWFDict(filename):
    with open(filename, 'r') as f:
        wf = json.load(f)
    return wf

def addToWFDict(wfTo, wfFrom):
    for key, value in wfFrom.items():
        if key in wfTo:
            wfTo[key] += value
        else:
            wfTo[key] = value

# deprecated
# allowedType : the list of allowed POS-tagger types
def mergeWFDict(allowedType):
    WFDict = dict()
    for type in allowedType:
        tmpDict = loadWFDict(WF_Folder + '%s_List.json' % (type))
        addToWFDict(WFDict, tmpDict)
    return WFDict

# filter the words in word-frequency dict, return a set of allowed words
def filteredByThreshold(WFDict, threshold):
    words = set()
    fSum = sum(WFDict.values())
    for w, f in WFDict.items():
        if float(f)/fSum >= threshold:
            words.add(w)
    return words

# get allowed words for each type of POS tagger,
# return a dict (pos-tagger -> set of allowed words)
def getAllowedWords(allowedPOSType, threshold, WFDictDict):
    allowedWords = dict()
    for type in allowedPOSType:
        allowedWords[type] = filterByThreshold(WFDictDict[type], threshold)
    return allowedWords

# list of parsedLabelNews: label & news 
# allowedWTList: allowed words for each kind of tag in each layer
#    allowedWTList[0]['NN']: the words allowed of NN in 0 layer (seed)
# allowedRelList: allowed dependency relations in each layer

def generateXY(parsedLabelNews, allowedWTList=[['NN','NR'], None, None], 
        allowedRelList=[None, None]):
    # check input
    if len(allowedWTList) != (len(allowedRelList)+1) :
        return None

    Y = list()
    XFeature = list()
    for labelNews in parsedLabelNews:
        title_dep = labelNews['news']['title_dep']
        content_dep = labelNews['news']['content_dep']
        
    

# TODO: calculate frequency from dependencies

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'parsedLabelNewsJson', file=sys.stderr)
        exit(-1)

    maxLayer = 1
    allowedPOSType = [['NN', 'NR'], ['VA', 'VV', 'JJ', 'AD']]

    # read all necessary word frequency dictionary
    WFDictDict = dict()
    for i in range(0, maxLayer+1):
        for type in allowedPOSType[i]:
            if type not in WFDictDict:
                WFDictDict[type] = loadWFDict(WF_Folder + '%s_List.json' % (type))

    # for each threshold
    for threshold in [0.5]:
        allowedWTList = [None for i in range(0, maxLayer+1)]
        # for each statId
        for statId in [2, 3, 4, 5, 6, 10, 13, 16]:
            # for each layer (including seed), generate allowed words
            for layer in range(0, maxLayer+1):
                allowedWTList[layer] = getAllowedWords(allowedPOSType[i], threshold, WFDictDict)
            
            # generate features
            generateXY(parsedLabelNews, allowedWTList)
                
            
    
