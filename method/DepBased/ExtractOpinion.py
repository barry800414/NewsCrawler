#!/usr/bin/env python3

import sys
import json

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
def countOpinions(opinions, opnCnt):
    for opnName, opns in opinions.items():
        if opnName not in opnCnt:
            opnCnt[opnName] = dict()
        for opn in opns:
            #TODO
            key = tuple(opn.keys())
        
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
        topicLabelNews = labelNewsInTopic[t]
        for labelNews in topicLabelNews[0:1]:
            opinions = extractOpinions(labelNews['news'], pTreeList, negPList)
        print(opinions)
