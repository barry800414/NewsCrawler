#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import dataTool
import TreePattern as TP
import DepTree as DT
import NegPattern as NP
from Opinion import *
from sentiDictSum import readSentiDict

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
                    del r['mapping']
                
                # convert to Opinion objects
                for i in range(0, len(results)):
                    results[i] = Opinion.genOpnFromDict(results[i])
            opnDict[pTree.name].extend(results)
    return opnDict


# opinons: a dictionary (opinion-type-name -> list of opinions)
# opnCnt: a dictionary (opinion-type-name -> a dictionary (opnKey -> count))
# keyType: 'HOT', 'HT', 'OT', 'HO', 'T', 'H'
# return: opinion-type-name -> a dict to count occurence of each opinions
def countOpinions(opinions, opnCnts, keyTypeList=['HOT'], sentiDict=None, negSepList=[False]):
    for opnName, opns in opinions.items():
        if opnName not in opnCnts:
            opnCnts[opnName] = defaultdict(int)

        for opn in opns:
            for keyType in keyTypeList:
                for negSep in negSepList:
                    (key, value) = getOpnKeyValue(opn, keyType, sentiDict, negSep)
                    opnCnts[opnName][key] += value
    return opnCnts


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

def printOpnCnt(opnCnts, outfile=sys.stdout):
    for opnName, opnCnt in opnCnts.items():
        print(opnName, file=outfile)
        for key, cnt in sorted(opnCnt.items(), key = lambda x:x[1], reverse=True):
            print(key, cnt, sep=',', file=outfile)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        #print('Usage:', sys.argv[0], 'depParsedLabelNewsJson phraseFile sentiDictFile', file=sys.stderr)
        print('Usage:', sys.argv[0], 'DepParsedLabelNews PatternFile NegPatternFile SentiDictFile', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    patternFile = sys.argv[2]
    negPatternFile = sys.argv[3]
    sentiDictFile = sys.argv[4]
    #phrasesJsonFile = sys.argv[4]

    # load label-news
    with open(parsedLabelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)

    # load pattern trees 
    pTreeList = TP.loadPatterns(patternFile)

    # load negation pattern file
    negPList = NP.loadNegPatterns(negPatternFile)

    # load phrases
    #topicPhraseList = loadPhraseFile(phrasesJsonFile)

    # load sentiment dictionary
    sentiDict = readSentiDict(sentiDictFile)

    # get the set of all possible topic
    topicSet = set([labelNews['statement_id'] for labelNews in labelNewsList])
    labelNewsInTopic = dataTool.divideLabel(labelNewsList)

    for t in topicSet:
        with open('opinions_topic%d.txt' % (t), 'w') as f:
            opnCnts = dict()
            topicLabelNews = labelNewsInTopic[t]
            for i, labelNews in enumerate(topicLabelNews):
                opnDict = extractOpinions(labelNews['news'], pTreeList, negPList)
                if i % 10 == 0:
                    print('Progress(%d/%d)' % (i+1, len(topicLabelNews)), file=sys.stderr) 
                countOpinions(opnDict, opnCnts, keyTypeList=['HOT', 'HT', 'OT', 'HO', 'H', 'T'], sentiDict=sentiDict)
            printOpnCnt(opnCnts, outfile=f)

