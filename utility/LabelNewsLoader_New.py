#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import MySQLdb
import json
from  time import *
import NewsLoader
import math

# filter the news with important keywords
class DataInconsistent():
    def __init__(self, db_info):
        self.connect_to_db(db_info)

    def connect_to_db(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def getStatementNews(self, statList):
        sql = 'SELECT * FROM statement_news where '
        for i, statId in enumerate(statList):
            if i == 0:
                sql = sql + ' statement_id = %d ' % statId
            else:
                sql = sql + ' OR statement_id = %d ' % statId
        print(sql)
        try: 
            self.cursor.execute(sql)
            lnList = list()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                ln = dict()
                ln['id'] = tmp[0]
                ln['statement_id'] = tmp[1]
                ln['news_id'] = tmp[2]
                ln['valid_format'] = tmp[3]
                ln['relevance'] = tmp[4]
                ln['mention_agree'] = tmp[5]
                ln['mention_disagree'] = tmp[6]
                ln['label'] = tmp[7]
                ln['labeler'] = tmp[8]
                ln['generated_time'] = tmp[9]
                lnList.append(ln)  
            return lnList
        except Exception, e:
            print e

    #snDict: key: statement_id & news_id, value: the list of statement news instance
    def toStatNewsDict(self, lnList):
        snDict = dict()
        for ln in lnList:
            s = ln['statement_id']
            n = ln['news_id']
            if (s, n) not in snDict:
                snDict[(s, n)] = list()
            snDict[(s, n)].append(ln)
        return snDict

    # detect duplicated statement-news (in short time)
    def detectDuplicate(self, snDict):
        for sn, lns in snDict.items():
            for i in range(0, len(lns)):
                ln1 = lns[i]
                for j in range(i+1, len(lns)):
                    ln2 = lns[j]
                    delta = ln1['generated_time'] - ln2['generated_time']
                    if abs(delta.total_seconds()) < 20:
                        print 'Duplicated:', ln1['statement_id'], ln1['news_id']
                        cmd = 'SELECT * FROM statement_news WHERE statement_id = %s and news_id = "%s"' % (ln1['statement_id'], ln2['news_id'])
                        print cmd

    # voting compare
    def detectValidFormat2(self, snDict):
        cnt = 0
        toRelabelSet = set()
        invalidSet = set()
        for sn, lns in snDict.items():
            labelCnt = { 'valid': 0, 'small_error': 0, 'invalid': 0 }
            for i in range(0, len(lns)):
                ln1 = lns[i]
                ln1v = ln1['valid_format']
                labelCnt[ln1v] += 1

            validCnt = labelCnt['valid'] + labelCnt['small_error'] 
            invalidCnt = labelCnt['invalid']
            #print(labelCnt, validCnt, invalidCnt)
            if validCnt == invalidCnt:
                print(sn)
                toRelabelSet.add(sn)
                cnt += 1
            elif invalidCnt > validCnt:
                invalidSet.add(sn)

        print "#valid format inconsistent:", cnt
        return (toRelabelSet, invalidSet)

    # voting compare
    def detectRelevance2(self, snDict, invalidSet):
        toRelabelSet = set()
        irrelSet = set()
        for sn, lns in snDict.items():
            labelCnt = { 'relevant': 0, 'irrelevant': 0, '': 0}
            for i in range(0, len(lns)):
                ln1 = lns[i]
                ln1r = ln1['relevance']
                labelCnt[ln1r] += 1

            if labelCnt['relevant'] == labelCnt['irrelevant'] and labelCnt['relevant'] != 0: 
                toRelabelSet.add(sn)
            elif labelCnt['relevant'] < labelCnt['irrelevant']:
                irrelSet.add(sn)

        toRelabelSet = toRelabelSet - invalidSet
        print "#Relevance inconsistent:", len(toRelabelSet)
        return (toRelabelSet, irrelSet)


    def removeInvalidAndIrrel(self, snDict):
        (relabelSet1, invalidSet) = self.detectValidFormat2(snDict)
        (relabelSet2, irrelSet) = self.detectRelevance2(snDict, invalidSet)
        print '#invalid:', len(invalidSet)
        print '#irrel:', len(irrelSet)
        assert len(relabelSet1) == 0 and len(relabelSet2) == 0
        u = invalidSet | irrelSet
        for key in u:
            del snDict[key]
        return snDict

    # relabel 
    def getLabelNewsList(self, newsLoader, statList):
        lnList = self.getStatementNews(statList)
        snDict = self.toStatNewsDict(lnList)
        self.detectDuplicate(snDict)

        print(len(snDict))
        snDict = self.removeInvalidAndIrrel(snDict)
        print(len(snDict))

        snDict = convertLabels(snDict)
        print len(snDict)
        labelNewsList = mergeLabel(snDict)

        return labelNewsList

def convertLabels(snDict):
    newDict = dict()
    for sn, labels in snDict.items():
        newLabels = list()
        for labelObj in labels:
            label = labelObj['label']
            if len(label) != 0:
                newLabels.append(label)
        if len(newLabels) != 0:
            newDict[sn] = newLabels
        else:
            print(labels)
    return newDict

# TODO: calculate statistics
def mergeLabel(snDict, method='vote'):
    # merge label
    mergeLabel = dict()
    cnt = 0
    cnt1 = 0
    for sn, labels in snDict.items():
        (majClass, maxPoll, numMax) = findMajorClass(labels)
        if numMax == 1:
            cnt += 1
            mergeLabel[sn] = majClass
        else:
            cnt1 += 1
            mergeLabel[sn] = getLabelByAvg(labels)
    print "mergeByMajorityClass:" + str(cnt)
    print "mergeByAverage:" + str(cnt1)

    
    # convert back to list of labels
    newList = list()
    for sn in mergeLabel.keys():
        label = mergeLabel[sn]
        labelDict = { 
            "label": label, 
            "statement_id" : sn[0],
            "news_id": sn[1],
        }
        newList.append(labelDict)
    return newList
            

def findMajorClass(labels):
    s2i = { "oppose": 0, "neutral": 1, "agree": 2 }
    i2s = { 0: "oppose", 1: "neutral", 2: "agree" }

    poll = [0 for i in range(0, len(s2i))]
    for label in labels:
        poll[s2i[label]] += 1

    maxPoll = None
    maxIndex = 0
    numMax = 0
    for i, p in enumerate(poll):
        if maxPoll == None:
            maxPoll = p
            maxIndex = i
            numMax = 1
        elif p > maxPoll:
            maxPoll = p
            maxIndex = i
            numMax = 1
        elif p == maxPoll:
            numMax += 1
    
    # (one of majority class, number of polls, number of majority class)
    return (i2s[maxIndex], maxPoll, numMax) 

def getLabelByAvg(labels):
    avg = calcAvg(labels)
    v2s = { -1: "oppose", 0: "neutral", 1:"agree" }
    return v2s[floatCmp(avg, 0.0)]

def calcAvg(labels):
    s2v = { "oppose":-1, "neutral": 0, "agree": 1 }
    avg = 0
    for label in labels:
        avg += s2v[label]
    avg = float(avg) / len(labels)
    return avg

def floatCmp(a, b):
    FLOAT_ERR = 1e-9
    if math.fabs(a - b) < FLOAT_ERR:
        return 0
    elif a > b:
        return 1
    else:
        return -1

'''
topic_json = {
    "src_table": "merge",
    "target_table": "topic_news_all",
    "topic_configs": [ topic_config1, topic_config2 ...]
}

topic_config = {
    "id": ...,
    "target_table": ...,
    "src_table": ...,
    "keywords": [...],
    "minimum_frequency": .. 
}
'''


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'db_info_json outJson'
        exit(-1)

    dbInfoJsonFile = sys.argv[1]
    labelLogFile = sys.argv[2]    

    with open(dbInfoJsonFile, 'r') as f:
        db_info = json.load(f)

    statList = [2, 3, 4, 5, 6, 13, 16]
    nl = NewsLoader.NewsLoader(db_info)
    di = DataInconsistent(db_info)
    labelNewsList = di.getLabelNewsList(nl, statList)

    with open(labelLogFile, 'w') as f:
        json.dump(labelNewsList, f, ensure_ascii=False, indent=2)
