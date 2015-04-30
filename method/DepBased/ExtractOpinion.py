#!/usr/bin/env python3

import sys
import json
from collections import defaultdict

import dataTool
import TreePattern as TP
import DepTree as DT
import NegPattern as NP

def extractOpinions(depParsedNews, pTreeList, negPList=None):
    opinions = dict()
    contentDep = depParsedNews['content_dep']
    for depObj in contentDep:
        tdList = depObj['tdList']
        depTree = DT.DepTree(tdList)
        for pTree in pTreeList:
            if pTree.name not in opinions:
                opinions[pTree.name] = list()
            results = pTree.match(depTree)
            if negPList != None:
                for r in results:
                    negCntDict = NP.checkAllNegPattern(negPList,
                            depTree, pTree, r['mapping'])
                    if len(negCntDict) > 0:
                        r['neg'] = negCntDict
                    del r['mapping']
            opinions[pTree.name].extend(results)
    return opinions

# opinons: opinion-type-name -> list of opinions
# output: opinion-type-name -> a dict to count occurence of each opinions
def countOpinions(opinions, opnCnts, opnColName):
    for opnName, opns in opinions.items():
        if opnName not in opnCnts:
            opnCnts[opnName] = defaultdict(int)
            if len(opns) != 0 and opnName not in opnColName:
                opnColName[opnName] = __genColKey(opns[0])
        for opn in opns:
            key = __genWordKey(opn)
            opnCnts[opnName][key] += 1

    return (opnCnts, opnColName)
        
def __genWordKey(opn):
    kList = list()
    sortItems = sorted(opn.items(), key=lambda x:x[0])
    if 'neg' in opn:
        for key, value in sortItems:
            if key == 'neg':
                continue
            neg = opn['neg'][key] if key in opn['neg'] else 0
            if neg != 0:
                kList.append('%s_negCnt%d' % (value, neg))
            else:
                kList.append(value)
    else:
        for key, value in sortItems:
            kList.append(value)
    return tuple(kList)

def __genColKey(opn):
    return sorted([k for k in opn.keys() if k != 'neg'])

def printOpnCnt(opnCnts, opnColName, outfile=sys.stdout):
    for opnName, opnCnt in opnCnts.items():
        print(opnName, file=outfile)
        if opnName in opnColName:
            print(opnColName[opnName], file=outfile)
        for key, cnt in sorted(opnCnt.items(), key = lambda x:x[1], reverse=True):
            print(key, cnt, sep=',', file=outfile)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        #print('Usage:', sys.argv[0], 'depParsedLabelNewsJson phraseFile sentiDictFile', file=sys.stderr)
        print('Usage:', sys.argv[0], 'DepParsedLabelNews PatternFile NegPatternFile', file=sys.stderr)
        exit(-1)

    parsedLabelNewsJsonFile = sys.argv[1] # dependency parsing
    patternFile = sys.argv[2]
    negPatternFile = sys.argv[3]
    #phrasesJsonFile = sys.argv[4]
    #sentiDictFile = sys.argv[5]

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
    #sentiDict = readSentiDict(sentiDictFile)

    # get the set of all possible topic
    topicSet = set([labelNews['statement_id'] for labelNews in labelNewsList])
    labelNewsInTopic = dataTool.divideLabel(labelNewsList)

    for t in topicSet:
        with open('opinions_topic%d.txt' % (t), 'w') as f:
            opnCnts = dict()
            opnColName = dict()
            topicLabelNews = labelNewsInTopic[t]
            for i, labelNews in enumerate(topicLabelNews):
                opinions = extractOpinions(labelNews['news'], pTreeList, negPList)
                if i % 10 == 0:
                    print('Progress(%d/%d)' % (i+1, len(topicLabelNews)), file=sys.stderr) 
                countOpinions(opinions, opnCnts, opnColName)
            printOpnCnt(opnCnts, opnColName, outfile=f)

