#!/usr/bin/env python3 
import sys
import json

from collections import defaultdict
from ConstTree import ConstTree
import LM
import dataTool

def extractPhrases(newsDict, allowedPhrases=set(['NP', 'VP'])):
    pCnt = dict()
    pList = list()
    cnt = 0
    skippedCnt = 0
    for newsId, news in newsDict.items():
        contentConst = news['content_constituent']
        for const in contentConst:
            nodes = toNodes(const['nodes'])
            edges = toEdges(const['edges'])
            if nodes == None or edges == None: #FIXME
                skippedCnt += 1
                continue
            tree = ConstTree(nodes, edges)
            phraseTrees = tree.getPhraseTrees(allowedLabelSet=allowedPhrases)
            
            for t in phraseTrees:
                p = t.getPhrase()
                pStr = p.getSepStr()
                pTag = p.getTag()
                if (pStr, pTag) not in pCnt:
                    pList.append(p)
                    pCnt[(pStr, pTag)] = 1
                else:
                    pCnt[(pStr, pTag)] += 1
                # for debugging
                #ConstTree.printTree(t)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress(%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)
        #if cnt == 2:
        #    break
    print('skippedCnt:', skippedCnt, file=sys.stderr)

    for p in pList:
        p.cnt = pCnt[(p.getSepStr(),p.getTag())]
    
    return pList

def toNodes(nodeLines):
    nodes = list()
    for line in nodeLines:
        entry = line.strip().split(' ')
        if len(entry) != 3: #FIXME
            return None
        nodes.append((int(entry[0]), entry[1], entry[2]))
    return nodes

def toEdges(edgeLines):
    edges = list()
    for line in edgeLines:
        entry = line.strip().split(' ')
        if len(entry) != 2:
            return None
        edges.append((int(entry[0]), int(entry[1])))
    return edges



# pList: phrase -> count
# lm: language model
def reRankPhrasesList(pList, lm, minCnt=1, minLength=1, outfile=sys.stdout):
    # extracting NP phrases
    sortedByCnt = sorted(pList, key=lambda x:x.cnt, reverse=True)

    # using N-gram model to re-rank the phrases
    for p in pList:
        p.logProb = lm.avgLogProb(p.getSepStr().split(' '))
    sortedByLogProb = sorted(pList, key=lambda x:x.logProb, reverse=True)
 
    # using above two rank to re-rank the phrases
    for p in pList:
        p.sumRank = 0
    for i, p in enumerate(sortedByCnt):
        p.sumRank += i
    for i, p in enumerate(sortedByLogProb):
        p.sumRank += i
    sortedBySumRank = sorted(pList, key=lambda x:x.sumRank)

    print('====sort by count====', file=outfile)
    for p in sortedByCnt:
        if len(p.getSepStr().strip().split(' ')) >= minLength and p.cnt >= minCnt:
            #print(p, p.cnt, p.logProb, p.sumRank, file=outfile)
            print(p.getSepStr(), file=outfile)

    '''
    print('====sort by Log Prob====', file=outfile)
    for p in sortedByLogProb:
        if len(p.getSepStr().strip().split(' ')) >= minLength and p.cnt >= minCnt:
            print(p, p.cnt, p.logProb, p.sumRank, file=outfile)

    print('====sort by sum of rank====', file=outfile)
    for p in sortedBySumRank:
        if len(p.getSepStr().strip().split(' ')) >= minLength and p.cnt >= minCnt:
            print(p, p.cnt, p.logProb, p.sumRank, file=outfile)
    '''

# filter out the unqualified phrases
def filterPhrase(pList, minCnt=2, minLength=2):
    newList = list()
    for p in pList:
        if len(p.getSepStr().strip().split(' ')) >= minLength and p.cnt >= minCnt:
            newList.append(p)
    return newList

def dividePhraseByTag(pList):
    pDict = dict()
    for p in pList:
        tag = p.getTag()
        if tag not in pDict:
            pDict[tag] = list()
        pDict[tag].append(p)
    
    return pDict




if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'ConstituentParsedNewsJsonFile outPhraseJsonFile', file=sys.stderr)
        exit(-1)

    parsedNewsJsonFile = sys.argv[1]
    outPhraseJsonFile = sys.argv[2]

    with open(parsedNewsJsonFile, 'r') as f:
        newsDict = json.load(f)


    minCnt = 2
    minLength = 2
    topicPList = dict()

    ###### extracting phrase ######
    
    pList = extractPhrases(newsDict, allowedPhrases=set(['NP']))
    corpus = LM.constParsedNewsDictToCorpus(newsDict)
    lm = LM.LM(corpus, n=2)
    with open('phrases_all.txt', 'w') as f:
        reRankPhrasesList(pList, lm, minCnt=1, minLength=1, outfile=f)
    topicPList['all'] = filterPhrase(pList, minCnt, minLength)
    
    
    ###### extracting phrase for each topic ######
    topicNewsDict = dataTool.divideNewsByTopic(newsDict)
    for topicId, tNewsDict in topicNewsDict.items():
        print(topicId)
        pList = extractPhrases(tNewsDict, allowedPhrases=set(['NP']))
        corpus = LM.constParsedNewsDictToCorpus(tNewsDict)
        lm = LM.LM(corpus, n=2)
        with open('phrases_topic%d.txt' % topicId, 'w') as f:
            reRankPhrasesList(pList, lm, minCnt=1, minLength=1, outfile=f)
        topicPList[topicId] = filterPhrase(pList, minCnt, minLength)

    # convert topicPList to array or dict for json output
    for topicId in topicPList.keys():
        pDict = dividePhraseByTag(topicPList[topicId])
        for tag, pList in pDict.items():
            for i in range(0, len(pList)):
                pList[i] = pList[i].getSepStr()
        topicPList[topicId] = pDict

    with open(outPhraseJsonFile, 'w') as f:
        json.dump(topicPList, f, ensure_ascii=False, indent = 2)
    
    
