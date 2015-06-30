#!/usr/bin/env python3

import sys
import json

def data_cleaning(labelNewsList, printInfo=False):
    labelSet = set(["neutral", "oppose", "agree"])
    #labelSet = set(["neutral", "oppose", "agree"])
    newList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in labelSet:
            newList.append(labelNews)
    return newList

def printStatInfo(labelNewsList):
    statSet = set() # total possible of statement_id
    stat = dict()
    for labelNews in labelNewsList:
        statSet.add(labelNews['statement_id'])
        stat[labelNews['statement_id']] = labelNews['statement']['original']

    num = dict() # calculate each number for each statement
    for statId in statSet:
        num[statId] = { "agree": 0, "oppose": 0, "neutral": 0, '': 0 }
    
    for labelNews in labelNewsList:
        num[labelNews['statement_id']][labelNews['label']] += 1

    agreeSum = 0
    neutralSum = 0
    opposeSum = 0
    noLabelSum = 0
    print('statement ID, statement, agree, neutral, oppose, noLabel, total',file=sys.stderr)
    for statId in statSet:
        agree = num[statId]['agree']
        neutral = num[statId]['neutral']
        oppose = num[statId]['oppose']
        noLabel = num[statId]['']
        total = agree + neutral + oppose + noLabel
        print('%d, %s, %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d' % (statId, 
            stat[statId], agree, 100*float(agree)/total, neutral, 100*float(neutral)/total, 
            oppose, 100*float(oppose)/total, noLabel, 100*float(noLabel)/total, total),  
            file=sys.stderr)
        #print('%d, %s, %.1f%%, %.1f%%, %.1f%%, %d' % (statId, stat[statId], 
        #    100*float(agree)/total, 100*float(neutral)/total, 
        #    100*float(oppose)/total, total), file=sys.stderr)
        agreeSum += agree
        neutralSum += neutral
        opposeSum += oppose
        noLabelSum += noLabel
    totalSum = agreeSum + neutralSum + opposeSum + noLabelSum
    print('Total, , %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d' % (
        agreeSum, 100*float(agreeSum)/totalSum, 
        neutralSum, 100*float(neutralSum)/totalSum, 
        opposeSum, 100*float(opposeSum)/totalSum, 
        noLabelSum, 100*float(noLabelSum)/totalSum, 
        totalSum),
        file=sys.stderr)
    #print('Total, , %.1f%%, %.1f%%, %.1f%%, %d' % (
    #    100*float(agreeSum)/totalSum, 
    #    100*float(neutralSum)/totalSum, 
    #    100*float(opposeSum)/totalSum, totalSum), file=sys.stderr)

# merge news file, label file, and statement file to one object
def mergeToLabelNews(labelList, newsDict, statDict, 
        newsCol=["content","title"], statCol=["original", "seg"], allowedStatIdSet=None):
    newList = list()
    for labelDict in labelList:
        newDict = dict(labelDict)
        statId = labelDict['statement_id']
        if allowedStatIdSet is not None and statId not in allowedStatIdSet:
            continue
        newsId = labelDict['news_id']
        if statId in statDict:
            sDict = dict()
            for c in statCol:
                sDict[c] = statDict[statId][c]
            newDict['statement'] = sDict
        else:
            print('%d not found in statement list' % statId, file=sys.stderr)
        if newsId in newsDict:
            nDict = dict()
            for c in newsCol:
                nDict[c] = newsDict[newsId][c]
            newDict['news'] = nDict
        else:
            print('%s not found in news corpus' % newsId, file=sys.stderr)
            continue
        newList.append(newDict)

    return newList


def divideLabel(labelNewsList):
    #FIXME stat and topic
    labelNewsInTopic = dict()
    for labelNews in labelNewsList:
        statId = labelNews['statement_id']
        if statId not in labelNewsInTopic:
            labelNewsInTopic[statId] = list()
        labelNewsInTopic[statId].append(labelNews)
    return labelNewsInTopic

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print('Usage:', sys.argv[0], 'labelJson NewsJson StatJson config outFile', file=sys.stderr)
        exit(-1)

    labelJsonFile = sys.argv[1]
    newsJsonFile = sys.argv[2]
    statJsonFile = sys.argv[3]
    configFile = sys.argv[4]
    outFile = sys.argv[5]

    with open(labelJsonFile, 'r') as f:
        labelList = json.load(f)
    with open(newsJsonFile, 'r') as f:
        newsDict = json.load(f)
    with open(statJsonFile, 'r') as f:
        tmpDict = json.load(f)
        statDict = dict()
        for key, value in tmpDict.items():
            statDict[int(key)] = value
    with open(configFile, 'r') as f:
        config = json.load(f)

    allowedStatIdSet = None
    if 'allowedStatementIdSet' in config:
        allowedStatIdSet = config['allowedStatementIdSet']

    labelNewsList = mergeToLabelNews(labelList, newsDict, statDict, 
            newsCol = config['news_column'], 
            statCol = config['statement_column'], 
            allowedStatIdSet = allowedStatIdSet)

    with open(outFile, 'w') as f:
        json.dump(labelNewsList, f, ensure_ascii=False, indent=2)

    print("#statement_news:", len(labelNewsList), file=sys.stderr)
    printStatInfo(labelNewsList)
    
