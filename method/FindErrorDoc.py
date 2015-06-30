
import sys, pickle, json
from collections import defaultdict

def getTopic(filename):
    s = filename.find('SelfTrainTest_topic')
    e = filename.find('.pickle')
    t = int(filename[s+len('SelfTrainTest_topic'): e])
    return t

def calcErrNewsCnt(p, newsTestCnt, newsErrCnt, t):
    X = p['data']['X']
    y = p['data']['y']
    newsIdList = p['newsIdList']
    logList = p['logList']
    for log in logList:
        clf = log['clf']
        testIndex = log['split']['testIndex']
        yTest = y[testIndex]
        yTestPredict = log['predict']['yTestPredict']
        assert len(yTest) == len(yTestPredict)
        for i in range(0, len(yTest)):
            newsId = newsIdList[testIndex[i]]
            if yTest[i] != yTestPredict[i]:
                newsErrCnt[newsId] += 1
            newsTestCnt[newsId] += 1
                

if len(sys.argv) != 4:
    print('Usage:', sys.argv[0], 'fileList lnJson_OriginalLabel lnJson_NowLabel', file=sys.stderr)
    exit(-1)

original = dict()
with open(sys.argv[2], 'r') as f:
    lnList = json.load(f)
for ln in lnList:
    t = ln['statement_id']
    newsId = ln['news_id']
    if t not in original:
        original[t] = dict()
    original[t][newsId] = ln['label']

newsDict = dict()
now = dict()
with open(sys.argv[3], 'r') as f:
    lnList = json.load(f)
for ln in lnList:
    t = ln['statement_id']
    newsId = ln['news_id']
    if t not in now:
        now[t] = dict()
    now[t][newsId] = ln['label']
    newsDict[newsId] = ln['news']

topicNewsErrCnt = dict()
topicNewsTestCnt = dict()
with open(sys.argv[1], 'r') as f:
    for line in f:
        filename = line.strip()
        t = getTopic(filename)
        if t not in topicNewsErrCnt:
            topicNewsTestCnt[t] = defaultdict(int)
            topicNewsErrCnt[t] = defaultdict(int)
        print('Loading pickle file:', filename, file=sys.stderr)
        with open(filename, 'r+b') as f:
            p = pickle.load(f)
        calcErrNewsCnt(p, topicNewsTestCnt[t], topicNewsErrCnt[t], t)

for t, testCnt in sorted(topicNewsTestCnt.items(), key=lambda x:x[0]):
    errRate = list()
    errCnt = topicNewsErrCnt[t]
    print('=======Topic:%d=======' % (t))
    for newsId, cnt in testCnt.items():
        if newsId in errCnt:
            errRate.append((newsId, cnt, errCnt[newsId], errCnt[newsId] / cnt))
        else:
            errRate.append((newsId, cnt, 0, 0.0))
    
    # sort by error rate (descending)
    errRate.sort(key=lambda x:x[3], reverse=True)
    for c in errRate:
        newsId = c[0]
        oriId = original[t][newsId] 
        nowId = now[t][newsId] 
        print(c[0], c[1], c[2], c[3], oriId, nowId)
        if c[3] > 0.9 or c[3] < 0.05:
            print(newsDict[newsId])
    print('---------------------------------------------------\n')
