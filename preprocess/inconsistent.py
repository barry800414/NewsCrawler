#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import MySQLdb
import json
from  time import *
import NewsLoader

class uColor:
    PURPLE = u'\033[1;35m'
    YELLOW = u'\033[1;33m'
    GREEN = u'\033[1;32m'
    RED = u'\033[1;31m'
    LIGHT_BLUE = u'\033[1;34m'
    NC = u'\033[0m' # no color

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

    def getStatementNews(self):
        sql = 'SELECT * FROM statement_news'
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

    def detectValidFormat(self, snDict):
        cnt = 0
        toRelabelSet = set()
        for sn, lns in snDict.items():
            for i in range(0, len(lns)):
                ln1 = lns[i]
                ln1v = ln1['valid_format']
                for j in range(0, len(lns)):
                    if i == j:
                        continue
                    ln2 = lns[j]
                    ln2v = ln2['valid_format']
                    if (ln1v == 'valid' or ln1v == 'small_error') and (ln2v == 'invalid'):
                        #print 'Valid Format Inconsistent(1: valid or small_error, 2:invalid): ', ln1['statement_id'], ln1['news_id'], len(lns)
                        cnt += 1
                        toRelabelSet.add(sn)
        print "#valid format inconsistent:", cnt
        return toRelabelSet

    def detectRelevance(self, snDict):
        cnt = 0
        toRelabelSet = set()
        for sn, lns in snDict.items():
            for i in range(0, len(lns)):
                ln1 = lns[i]
                ln1r = ln1['relevance']
                for j in range(0, len(lns)):
                    if i == j:
                        continue
                    ln2 = lns[j]
                    ln2r = ln2['relevance']
                    if ln1r == 'relevant' and (ln2r == 'irrelevant' or ln2r == ''):
                        #print 'Relevance Inconsistent(1: relevant, 2:irrelevant): ', ln1['statement_id'], ln1['news_id'], len(lns)
                        cnt += 1
                        toRelabelSet.add(sn)
        print "#Relevance inconsistent:", cnt
        return toRelabelSet

    def labelValid(self):
        msg = uColor.PURPLE + u"格式正確性:" + uColor.NC + u"(1)內文無錯誤 (2)內文有些許錯誤，但不致於影響閱讀 (3)內文有較大錯誤（例如段落遺失、大量廣告文字、亂碼等等）:"
        while True:
            print msg,
            input = raw_input("").strip()
            if input not in ['1', '2', '3']:
                print uColor.RED + u'輸入錯誤, 請重新輸入 1、2 或3' + uColor.NC
            else:
                break
        mapping = ["valid", "small_error", "invalid"]
        return mapping[int(input) - 1]
        
    def labelRelevance(self, topicName):
        msg = uColor.PURPLE + u"文章與主題相關性:" + uColor.NC + u"(1)本篇文章 與「%s」高度相關 (2)本篇文章 與「%s」無相關或不太相關:" % (topicName, topicName)
        while True:
            print msg,
            input = raw_input("").strip()
            if input not in ['1', '2']:
                print uColor.RED + u'輸入錯誤, 請重新輸入 1或2' + uColor.NC 
            else:
                break
        mapping = ["relevant", "irrelevant"]
        return mapping[int(input) - 1]

    def labelMention(self, statId):
        stat = self.getStatement(statId)
        msg = uColor.PURPLE + u"文章提及正反意見:" + uColor.NC + u"(1)提及支持「%s」之論述 (2)提及反對「%s」之論述\n" % (stat, stat)
        msg += u"(本問題為複選題, 可回答 1 或 2 或 1 2 或空白):"
        while True:
            print msg,
            input = raw_input("").strip()
            if input not in ['', '1', '2', '1 2']:
                print uColor.RED + u'輸入錯誤, 請重新輸入 1或2' + uColor.NC
            else:
                break
        
        if input == '':
            return ("no", "no")
        elif input == '1':
            return ("yes", "no")
        elif input == '2':
            return ("no", "yes")
        elif input == '1 2':
            return ("yes", "yes")

    def labelStance(self, statId):
        stat = self.getStatement(statId)
        msg = uColor.PURPLE + u"整體立場:" + uColor.NC + u"(1)支持「%s」 (2)中立  (3)反對「%s」:" % (stat, stat)
        while True:
            print msg,
            input = raw_input("").strip()
            if input not in ['1', '2', '3']:
                print uColor.RED + u'輸入錯誤, 請重新輸入 1、2或3' + uColor.NC
            else:
                break
        mapping = ["agree", "neutral", "oppose"]
        return mapping[int(input) - 1]

    # get the labeled statement-news by this console
    def getLabeledSet(self):
        sql = "SELECT statement_id, news_id FROM `statement_news` WHERE labeler = 'console'" 
        try: 
            self.cursor.execute(sql)
            labeledSet = set()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                labeledSet.add((ln[0], ln[1]))
            return labeledSet
        except Exception, e:
            print e
            return None

    def getTopicName(self, statId):
        sql = "SELECT B.name FROM `statement` as A, `topic` as B WHERE A.topic_id = B.id " 
        try: 
            self.cursor.execute(sql + ' AND A.id = %s', (statId,))
            r = self.cursor.fetchone()
            return r[0]
        except Exception, e:
            print e
            return None

    def getStatement(self, statId):
        sql = "SELECT content FROM `statement` "
        try: 
            self.cursor.execute(sql + ' WHERE id=%s', (statId,))
            r = self.cursor.fetchone()
            return r[0]
        except Exception, e:
            print e
            return None

    def startLabel(self, toRelabelSet, newsLoader):
        results = dict()
        print "# to relabel:", len(toRelabelSet)
        for sn in toRelabelSet:
            r = self.labelOneStatNews(sn[0], sn[1], newsLoader)    
            results[sn] = r
            print '==================================================================================\n'
            print uColor.YELLOW + u"繼續標記下一篇? (Y/N default:Y):" + uColor.NC, 
            input = raw_input("").strip()
            if input == 'n' or input == 'N':
                print uColor.RED + u"標記結束" + uColor.NC
                break
        return results

    def labelOneStatNews(self, statId, newsId, newsLoader):
        news = newsLoader.getNews(newsId, "merge_necessary_clean")
        topicName = self.getTopicName(statId)
        stat = self.getStatement(statId)
        print '=================================================================================='
        print uColor.YELLOW + u"主題:" + uColor.NC + topicName
        print uColor.GREEN + u"標題:" + uColor.NC + news['title']
        print uColor.LIGHT_BLUE + u"內文:" + uColor.NC + news['content'] + u'\n'
        
        r = dict()

        r['valid_format'] = self.labelValid()
        if r['valid_format'] == 'invalid':
            print uColor.RED + u"文章格式錯誤，不必再標記" + uColor.NC
            return r
        r['relevance'] = self.labelRelevance(topicName)
        if r['relevance'] == 'irrelevant':
            print uColor.RED + u"文章與主題不相關，不必再標記" + uColor.NC
            return r
        r['mention_agree'], r['mention_disagree'] = self.labelMention(statId)
        r['label'] = self.labelStance(statId)
        return r

    # detect all kinds of data inconsistency
    def detect(self):
        lnList = self.getStatementNews()
        snDict = self.toStatNewsDict(lnList)
        self.detectDuplicate(snDict)
        self.detectValidFormat(snDict)
        self.detectRelevance(snDict)

    # relabel 
    def relabel(self, newsLoader):
        lnList = self.getStatementNews()
        snDict = self.toStatNewsDict(lnList)
        s1 = self.detectValidFormat(snDict)
        s2 = self.detectRelevance(snDict)
        labeledSet = self.getLabeledSet()
        toRelabelSet = (s1 | s2) - labeledSet
        self.startLabel(toRelabelSet, newsLoader)

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
    if len(sys.argv) != 2:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'db_info_json'
        exit(-1)

    db_info_json_file = sys.argv[1]

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    nl = NewsLoader.NewsLoader(db_info)
    di = DataInconsistent(db_info)
    di.relabel(nl)
