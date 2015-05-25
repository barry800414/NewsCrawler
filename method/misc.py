
import json
import sys
import random

label2i = { "neutral" : 2, "oppose": 0, "agree" : 1 } 
i2Label = ["oppose", "agree", "neutral"]

def toStr(v, sep='**', ensure_ascii=True):
    outStr = json.dumps(v, ensure_ascii=ensure_ascii)
    outStr = outStr.replace(',', sep)
    return outStr

def str2Var(inStr, sep='**'):
    return json.loads(inStr.replace(sep, ','))

def toFStr(v):
    outStr = json.dumps(v)
    outStr = outStr.replace("'", '')
    outStr = outStr.replace('"', '')
    outStr = outStr.replace(',', '')
    outStr = outStr.replace(' ', '')
    return outStr

# volc: volc -> index (dict)
# rVolc: index -> volc (list)
def reverseVolc(volc):
    rVolc = [None for i in range(0, len(volc))]
    for v, i in volc.items():
        rVolc[i] = v
    return rVolc

# merge two volcabulary
# 0~len(volc1)-1 for volc1
# len(volc1) ~ len(volc1)+len(volc2) -1 for volc2
def mergeVolc(volc1, volc2):
    volc3 = dict(volc1)
    offset = len(volc1)
    for key, value in volc2.items():
        volc3[key] = value + offset
    return volc3

def getFileNamePrefix(path):
    s = path.rfind('/')
    e = path.rfind('.')
    if s != -1:
        if e != -1 and e != 0:
            name = path[s+1:e]
        else:
            name = path[s+1:]
    else:
        if e != -1 and e != 0:
            name = path[:e]
        else:
            name = path
    return name

#print(getFileNamePrefix('./word/123.an'))
#print(getFileNamePrefix('123.an'))
#print(getFileNamePrefix('./word/123'))
#print(getFileNamePrefix('123'))

# get labels from the list of label-news
def getLabels(labelNewsList, mapping=label2i):
    labelList = list()
    for labelNews in labelNewsList:
        if labelNews['label'] in mapping:
            labelList.append(mapping[labelNews['label']])
    return labelList

def divideNewsByTopic(newsDict):
    topicNews = dict()
    for newsId, news in newsDict.items():
        topics = news['topic']
        for t in topics:
            if t not in topicNews:
                topicNews[t] = dict()
            topicNews[t][newsId] = news
    return topicNews

def divideLabelNewsByTopic(labelNewsList):
    #FIXME stat and topic
    labelNewsInTopic = dict()
    for labelNews in labelNewsList:
        statId = labelNews['statement_id']
        if statId not in labelNewsInTopic:
            labelNewsInTopic[statId] = list()
        labelNewsInTopic[statId].append(labelNews)
    return labelNewsInTopic


# return a dict (word -> sentiment score)
def readSentiDict(filename):
    sentiDict = dict()
    dupSet = set()
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            entry = line.strip().split(',')
            if len(entry) != 2:
                print('Line %d format error:' %(i+1), entry, file=sys.stderr)
                continue
            w = entry[0]
            s = int(entry[1])
            if w in sentiDict:
                #print(w, 'is already in dictionary', file=sys.stderr)
                dupSet.add(w)
            else:
                sentiDict[w] = s

    for w in dupSet:
        del sentiDict[w]
    return sentiDict

# docs is a list of label-news under certain topic
# docNum is a dict (className -> number, e.g. "agree" -> 100) 
def sampleDoc(docs, docNum, randSeed=1):
    assert sum(docNum.values()) <= len(docs)
    index = [i for i in range(0, len(docs))]
    
    random.seed(randSeed)
    random.shuffle(index)
    nowNum = { c: 0 for c in docNum.keys() }

    newDocs = list()
    for i in index:
        c = docs[i]['label']
        if nowNum[c] < docNum[c]:
            newDocs.append(docs[i])
            #newDocs.append(i)
            nowNum[c] += 1
    #print(newDocs)
    for c in docNum.keys():
        assert nowNum[c] == docNum[c]

    return newDocs

def printStatInfo(labelNewsList):
    statSet = set() # total possible of statement_id
    stat = dict()
    for labelNews in labelNewsList:
        statSet.add(labelNews['statement_id'])
        stat[labelNews['statement_id']] = labelNews['statement']['original']

    num = dict() # calculate each number for each statement
    for statId in statSet:
        num[statId] = { "agree": 0, "oppose": 0, "neutral": 0 }
    
    for labelNews in labelNewsList:
        num[labelNews['statement_id']][labelNews['label']] += 1

    agreeSum = 0
    neutralSum = 0
    opposeSum = 0
    docNum = { statId:dict() for statId in statSet }
    print('statement ID, statement, agree, neutral, oppose, total',file=sys.stderr)
    for statId in statSet:
        agree = num[statId]['agree']
        neutral = num[statId]['neutral']
        oppose = num[statId]['oppose']
        docNum[statId]['agree'] = agree
        docNum[statId]['neutral'] = neutral
        docNum[statId]['oppose'] = oppose
        total = agree + neutral + oppose
        print('%d, %s, %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d' % (statId, stat[statId], 
            agree, 100*float(agree)/total, neutral, 100*float(neutral)/total, 
            oppose, 100*float(oppose)/total, total), file=sys.stderr)
        #print('%d, %s, %.1f%%, %.1f%%, %.1f%%, %d' % (statId, stat[statId], 
        #    100*float(agree)/total, 100*float(neutral)/total, 
        #    100*float(oppose)/total, total), file=sys.stderr)
        agreeSum += agree
        neutralSum += neutral
        opposeSum += oppose
    totalSum = agreeSum + neutralSum + opposeSum
    print('Total, , %d(%.1f%%), %d(%.1f%%), %d(%.1f%%), %d' % (agreeSum, 
        100*float(agreeSum)/totalSum, neutralSum, 
        100*float(neutralSum)/totalSum, opposeSum, 
        100*float(opposeSum)/totalSum, totalSum), file=sys.stderr)
    #print('Total, , %.1f%%, %.1f%%, %.1f%%, %d' % (
    #    100*float(agreeSum)/totalSum, 
    #    100*float(neutralSum)/totalSum, 
    #    100*float(opposeSum)/totalSum, totalSum), file=sys.stderr)
    
    return docNum
