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
def generateXY(parsedLabelNews, allowedWTList, allowedRelList):
    # check input
    #if len(allowedWTList) != (len(allowedRelList)+1) :
        #return None

    maxLayer = len(allowedWTList) - 1
    Y = list()
    XFeature = list()
    volc = dict()
    for labelNews in parsedLabelNews:
        #titleDep = resetDep(labelNews['news']['title_dep'])
        contentDep = resetDep(labelNews['news']['content_dep'])
        
        allDepWTList = list()
        allGovWTList = list()
        for layer in range(0, maxLayer):
            # extraction
            DepWTList = searchGovToDep(contentDep, allowedWTList[layer], 
                    allowedDepWT=allowedWTList[layer+1]) 
            GovWTList = searchDepToGov(contentDep, allowedWTList[layer],
                    allowedGovWT=allowedWTList[layer+1])
            
            # add new words to seed word collection


            # save
            allDepWTList.append(DepWTList)
            allGovWTList.append(GovWTList)

#TODO: convert dep list to dep graph     
def resetDep(depList):
    for dep in depList:
        dep['traversed'] = False
    return depList
        
# govToDepConfig = [seedGovWT, allowedRel, allowedDepWT]
def searchGovToDep(depList, seedGovWT, allowedRel=None, allowedDepWT=None):
    WTList = list()
    for dep in depList:
        if dep['traversed']:
            continue

        (rel, gP, gW, gT, dP, dW, dT) = dep['tdList'].split(" ")
        
        # check whether dependencies obey the rules
        if gT not in seedGovWT:
            continue
        elif gW not in seedGovWT[gT]:
            continue
        if allowedRel != None:
            if rel not in allowedRel:
                continue
        if allowedDepWR != None:
            if dT not in allowedDepWR:
                continue
            elif dW not in allowedDepWR[dT]:
                continue

        # pass the checking, extract words & tags
        WTList.append((gW, gT, dW, dT))
    
        # mark the dependency relation as "USED"
        dep['traversed'] = True

    return WTList 

# depToGovConfig = [seedDepWT, allowedRel, allowedGovWT]
def searchDepToGov(depList, seedDepWT, allowedRel=None, allowedGovWT=None):
    WTList = list()
    for dep in depList:
        if dep['traversed']:
            continue

        (rel, gP, gW, gT, dP, dW, dT) = dep['tdList'].split(" ")
        
        # check whether dependencies obey the rules
        if dT not in seedDepWT:
            continue
        elif dW not in seedDepWT[gT]:
            continue
        if allowedRel != None:
            if rel not in allowedRel:
                continue
        if allowedGovWR != None:
            if gT not in allowedGovWR:
                continue
            elif gW not in allowedGovWR[dT]:
                continue

        # pass the checking, extract words & tags
        WTList.append((dW, dT, gW, gT))
    
        # mark the dependency relation as "USED"
        dep['traversed'] = True

    return WTList 




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
                
            
    
