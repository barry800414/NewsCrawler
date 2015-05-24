
import json

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

def divideLabel(labelNewsList):
    #FIXME stat and topic
    labelNewsInTopic = dict()
    for labelNews in labelNewsList:
        statId = labelNews['statement_id']
        if statId not in labelNewsInTopic:
            labelNewsInTopic[statId] = list()
        labelNewsInTopic[statId].append(labelNews)
    return labelNewsInTopic
