
import sys
import json

from collections import defaultdict
from ConstTree import ConstTree
import LM
import dataTool

def extractPhrases(newsDict, allowedPhrases=set(['NP', 'VP'])):
    phrasesCnt = defaultdict(int)
    cnt = 0
    skippedCnt = 0
    for newsId, news in newsDict.items():
        contentConst = news['content_constituent']
        for const in contentConst:
            nodes = toNodes(const['nodes'])
            edges = toEdges(const['edges'])
            if nodes == None or edges == None:
                skippedCnt += 1
                continue
            tree = ConstTree(nodes, edges)
            phraseTrees = tree.getPhraseTrees(allowedLabelSet=allowedPhrases)
            
            for t in phraseTrees:
                phrase = ConstTree.mergeWords(t)
                phrasesCnt[phrase] += 1
                # for debugging
                #ConstTree.printTree(t)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress(%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)
        #if cnt == 2:
        #    break
    print('skippedCnt:', skippedCnt, file=sys.stderr)
    return phrasesCnt


# phraseCnt: phrase -> count
# lm: language model
def reRankPhrasesList(phraseCnt, lm, minCnt=2, minLength=2, outfile=sys.stdout):
    # extracting NP phrases
    sortedByCnt = sorted(phraseCnt.items(), key=lambda x:x[1], reverse=True)

    # using N-gram model to re-rank the phrases
    phraseLogProb = dict()
    for phrase in phraseCnt.keys():
        phraseLogProb[phrase] = lm.avgLogProb(phrase.strip().split(' '))
    sortedByLogProb = sorted(phraseLogProb.items(), key=lambda x:x[1], reverse=True)
 
    # using above two rank to re-rank the phrases
    phraseSumRank = {phrase:0 for phrase in phraseCnt.keys()}
    for i, (p,cnt) in enumerate(sortedByCnt):
        phraseSumRank[p] += i
    for i, (p, logProb) in enumerate(sortedByLogProb):
        phraseSumRank[p] += i
    sortedBySumRank = sorted(phraseSumRank.items(),key=lambda x:x[1])

    print('====NP sort by count====', file=outfile)
    for phrase, cnt in sortedByCnt:
        if len(phrase.strip().split(' ')) >= minLength and cnt >= minCnt:
            print(phrase, cnt, phraseLogProb[phrase], phraseSumRank[phrase], file=outfile)

    print('====NP sort by Log Prob====', file=outfile)
    for phrase, lp in sortedByLogProb:
        cnt = phraseCnt[phrase]
        if len(phrase.strip().split(' ')) >= minLength and cnt >= minCnt:
            print(phrase, phraseCnt[phrase], lp, phraseSumRank[phrase], file=outfile)

    print('====NP sort by sum of rank====', file=outfile)
    for phrase, rp in sortedBySumRank:
        cnt = phraseCnt[phrase]
        if len(phrase.strip().split(' ')) >= minLength and cnt >= minCnt:
            print(phrase, phraseCnt[phrase], phraseLogProb[phrase], rp, file=outfile)


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

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'ConstituentParsedNewsJsonFile', file=sys.stderr)
        exit(-1)

    parsedNewsJsonFile = sys.argv[1]

    with open(parsedNewsJsonFile, 'r') as f:
        newsDict = json.load(f)

    ###### extracting phrase for all topics ######
    
    phraseCnt = extractPhrases(newsDict, allowedPhrases=set(['VP']))
    corpus = LM.constParsedNewsDictToCorpus(newsDict)
    lm = LM.LM(corpus, n=2)
    with open('phrases_all.txt', 'w') as f:
        reRankPhrasesList(phraseCnt, lm, minCnt=1, minLength=2, outfile=f)
    
    ###### extracting phrase for all topics ######
    topicNewsDict = dataTool.divideNewsByTopic(newsDict)

    for topicId, tNewsDict in topicNewsDict.items():
        phraseCnt = extractPhrases(tNewsDict, allowedPhrases=set(['VP']))
        corpus = LM.constParsedNewsDictToCorpus(tNewsDict)
        lm = LM.LM(corpus, n=2)
        with open('phrases_topic%d.txt' % topicId, 'w') as f:
            reRankPhrasesList(phraseCnt, lm, minCnt=1, minLength=2, outfile=f)


