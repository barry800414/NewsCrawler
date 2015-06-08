#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import TreePattern as TP
import DepTree as DT
import NegPattern as NP
from Opinion import *
from misc import *

# depParsedNews: dependency parsed news 
# pTreeList: pattern tree list
# negPList: negation pattern list
#
# return: a dictionary (opinion-type-name -> list of opinions)
def extractOpinions(depParsedNews, pTreeList, negPList=None):
    opnDict = dict()
    contentDep = depParsedNews['content_dep']
    
    # for each dependency tree
    for depObj in contentDep:
        tdList = depObj['tdList']
        depTree = DT.DepTree(tdList)
        # for each pattern tree
        for pTree in pTreeList:
            if pTree.name not in opnDict:
                opnDict[pTree.name] = list()
            results = pTree.match(depTree) # a list of opinions (dict)
            if negPList != None:
                # find negation pattern
                for r in results:
                    negCntDict = NP.checkAllNegPattern(negPList,
                            depTree, pTree, r['mapping'])
                    if len(negCntDict) > 0:
                        r['neg'] = negCntDict
                
                # convert to Opinion objects
                for i in range(0, len(results)):
                    opn = Opinion.genOpnFromDict(results[i], None)
                    opn.oriStr = depTree.getColoredStr(results[i]['mapping'].values()) # store the original string
                    results[i] = opn
            opnDict[pTree.name].extend(results)
    return opnDict


# opinons: a dictionary (opinion-type-name -> list of opinions)
# opnCnt: a dictionary (opinion-type-name -> a dictionary (opnKey -> count))
# keyType: 'HOT', 'HT', 'OT', 'HO', 'T', 'H'
# return: opinion-type-name -> a dict to count occurence of each opinions
def countOpinions(opinions, opnCnts, opnStrs, keyTypeList=['HOT'], sentiDict=None, negSepList=[False]):
    for opnName, opns in opinions.items():
        if opnName not in opnCnts:
            opnCnts[opnName] = defaultdict(int)
        if opnName not in opnStrs:
            opnStrs[opnName] = dict()

        for opn in opns:
            for keyType in keyTypeList:
                for negSep in negSepList:
                    keyValue = getOpnKeyValue(opn, keyType, sentiDict, negSep)
                    if keyValue is not None:
                        (key, value) = keyValue                    
                        opnCnts[opnName][key] += value
                        if key not in opnStrs[opnName]:
                            opnStrs[opnName][key] = list()
                        opnStrs[opnName][key].append(opn.oriStr)

    return (opnCnts, opnStrs)


def getOpnKeyValue(opn, keyType, sentiDict=None, negSep=False):
    if keyType == 'HT' or keyType == 'T' or keyType == 'H':
        assert sentiDict != None
    
    if keyType == 'HOT':
        return opn.getKeyHOT(negSep)
    elif keyType == 'HT':
        return opn.getKeyHT(sentiDict, negSep)
    elif keyType == 'H':
        return opn.getKeyH(sentiDict, negSep)
    elif keyType == 'HO':
        return opn.getKeyHO(negSep)
    elif keyType == 'OT':
        return opn.getKeyOT(negSep)
    elif keyType == 'T':
        return opn.getKeyT(sentiDict, negSep)

def printOpnCnt(opnCnts, opnStrs=None, outfile=sys.stdout):
    for opnName, opnCnt in opnCnts.items():
        print('-----', opnName, '-----' , file=outfile)
        for key, cnt in sorted(opnCnt.items(), key = lambda x:x[1], reverse=True):
            print(key, cnt, sep=':', file=outfile)
            if opnStrs is not None:
                for str in opnStrs[opnName][key]:
                    print(str, end=',', file=outfile)
                print('', file=outfile)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage:', sys.argv[0], 'DepParsedLabelNews PatternFile NegPatternFile SentiDictFile [-negSep] [-keyType ...]', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    patternFile = sys.argv[2]
    negPatternFile = sys.argv[3]
    sentiDictFile = sys.argv[4]
    negSep = False
    keyTypeList = list()
    for i in range(5, len(sys.argv)):
        if sys.argv[i] == '-negSep':
            print('Negative separate', file=sys.stderr)
            negSep = True
        elif sys.argv[i] == '-keyType':
            for j in range(i+1, len(sys.argv)):
                if sys.argv[j][0] == '-':
                    break
                elif sys.argv[j] not in ["H", "HT", "HOT", "T", "OT", "HO"]:
                    break
                keyTypeList.append(sys.argv[j])
            print('KeyTypeList:', keyTypeList, file=sys.stderr)

    # load label-news
    with open(parsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    # get the set of all possible topic
    topicSet = set([labelNews['statement_id'] for labelNews in labelNewsList])
    labelNewsInTopic = divideLabelNewsByTopic(labelNewsList)
    # load pattern trees 
    pTreeList = TP.loadPatterns(patternFile)
    # load negation pattern file
    negPList = NP.loadNegPatterns(negPatternFile)
    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)


    for t in topicSet:
        with open('opinions_topic%d.txt' % (t), 'w') as f:
            opnCnts = dict()
            opnStrs = dict()
            topicLabelNews = labelNewsInTopic[t]
            for i, labelNews in enumerate(topicLabelNews):
                opnDict = extractOpinions(labelNews['news'], pTreeList, negPList)
                if (i+1) % 10 == 0:
                    print('%cTopic%d: Progress(%d/%d)' % (13, t, i+1, len(topicLabelNews)), end='',  file=sys.stderr)
                countOpinions(opnDict, opnCnts, opnStrs, keyTypeList=keyTypeList, sentiDict=sentiDict, negSepList=[negSep])
            #printOpnCnt(opnCnts, outfile=f)
            printOpnCnt(opnCnts, opnStrs, outfile=f)
        print('', file=sys.stderr)

