#!/usr/bin/env python

import sys
import MySQLdb
import json
import codecs
import traceback

class NewsLoader():
    def __init__(self, db_info, table_info=None):
        self.connectToDB(db_info)
        if table_info != None:
            self.topicNewsTable = table_info['topic_news_table']
            #self.topicTable = table_info['topic_table']
        
    def connectToDB(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def convertToSql(self, column, prefix=None):
        s = ''
        if prefix != None:
            for c in column[0:-1]:
                s = s + '%s.%s, ' % (prefix, c)
            s = s + '%s.%s' % (prefix, column[-1])
        else:
            for c in column[0:-1]:
                s = s + '%s, ' % (c)
            s = s + '%s' % (column[-1])
        return s

    # get one piece of news from given table
    def getNews(self, newsId, corpusTable, newsColumns = ['title', 'content']):
        sql = 'SELECT %s FROM %s' % (self.convertToSql(newsColumns), corpusTable)
        try:
            self.cursor.execute(sql + ' WHERE id=%s', (newsId, ))
            tmp = self.cursor.fetchone()
            if tmp == None:
                return None
            else:
                news = dict()
                for i, c in enumerate(newsColumns):
                    news[c] = tmp[i]
                return news
        except Exception as e:
            print traceback.format_exc()
            return None

    def genWhereClause(self, topicIdList, limitNum):
        # select news of all possible topics
        sql = ''
        for i, topicId in enumerate(topicIdList):
            if i == 0:
                sql = sql + ' AND (A.topic_id = %d' % topicId
            else:
                sql = sql + ' OR A.topic_id = %d' % topicId
            if i == len(topicIdList) - 1:
                sql = sql + ')'
        if limitNum != -1:
            sql = sql + ' LIMIT 0, %s' % (limitNum)
        return sql

    # get news from given topic and given table
    def getNewsByTopic(self, topicIdList, limitNum, corpusTable, 
            newsColumns = ['title', 'content']):
        sql = '''
            SELECT DISTINCT A.news_id, %s FROM %s as A, %s as C
            WHERE A.news_id = C.id %s
        ''' % (self.convertToSql(newsColumns, 'C'), self.topicNewsTable, 
                corpusTable, self.genWhereClause(topicIdList, limitNum))
        
        try:
            print(sql)
            #execute the sql 
            self.cursor.execute(sql)
            
            #fetch rows
            newsDict = dict()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    news = dict()
                    newsId = tmp[0]
                    for i, c in enumerate(newsColumns):
                        news[c] = tmp[i+1]
                    newsDict[newsId] = news
            return newsDict
        except Exception as e:
            print traceback.format_exc()
            return None
    
    # get topic news from given topic and given table
    # topicNewsDict[topicId] is a list of topicNews
    # topicNews['topicNewsId'] is the id of topicNews
    # topicNews['news'] is the news
    def getTopicNews(self, topicIdList, limitNum, corpusTable, 
            newsColumns = ['title', 'content']):
        sql = '''
            SELECT A.id, A.topic_id, A.news_id, %s FROM %s as A, %s as C
            WHERE A.news_id = C.id %s
        ''' % (self.convertToSql(newsColumns, 'C'), self.topicNewsTable, 
                 corpusTable, self.genWhereClause(topicIdList, limitNum))
        
        try:
            print(sql)
            #execute the sql 
            self.cursor.execute(sql)
            
            #fetch rows
            topicNewsDict = dict()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    news = dict()
                    topicNewsId = tmp[0]
                    topicId = tmp[1]
                    news['id'] = tmp[2]
                    for i, c in enumerate(newsColumns):
                        news[c] = tmp[i+3]
                    if topicId not in topicNewsDict:
                        topicNewsDict[topicId] = list()
                    topicNewsDict[topicId].append({"topicNewsId": topicNewsId, "news": news})
            return topicNewsDict
        except Exception as e:
            print traceback.format_exc()
            return None


    def getTopic(self, newsId, limitTopics):
        sql = "SELECT topic_id FROM %s WHERE news_id='%s'" % (
                self.topicNewsTable, newsId)
        for i, topicId in enumerate(limitTopics):
            if i == 0:
                sql = sql + ' AND (topic_id = %d' % (topicId)
            else:
                sql = sql + ' OR topic_id = %d' % (topicId)
            if i == len(limitTopics) - 1:
                sql = sql + ')'
        #print(sql)
        try:
            self.cursor.execute(sql)
            topics = list()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    topics.append(int(tmp[0]))
            return topics
        except:
            print traceback.format_exc()
            return None


    def dumpNews(self, filename, newsList):
        # output as utf-8 file
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            json.dump(newsList, f, ensure_ascii=False, indent=2, sort_keys=True)


'''
news_loader_json = {
    "topicNewsTable": "topic_news",
    "topicTable": "topic",
    "corpus_table": "merge",
    "topic_id": 1,
    "news_id": ["setn0000001"], 
    "query_type" : "topic/news",
    "limit_num": 300
}
'''

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'news_loader_json db_info_json outputJsonFile'
        exit(-1)

    newsLoaderJsonFile = sys.argv[1]
    dbInfoJsonFile = sys.argv[2]
    outputJsonFile = sys.argv[3]

    with open(newsLoaderJsonFile, 'r') as f:
        newsLoaderConfig = json.load(f)

    with open(dbInfoJsonFile, 'r') as f:
        db_info = json.load(f)

    loader = NewsLoader(db_info, newsLoaderConfig)
    if newsLoaderConfig['query_type'] == 'topic':
        topicIdList = newsLoaderConfig['topic_id']
        limitNum = newsLoaderConfig['limit_num']
        corpusTable = newsLoaderConfig['corpus_table']
        # return a dict of news (news_id -> news content)
        newsDict = loader.getNewsByTopic(topicIdList, limitNum, corpusTable)
    elif newsLoaderConfig['query_type'] == 'news':
        newsIdList = newsLoaderConfig['news_id']
        corpusTable = newsLoaderConfig['corpus_table']
        newsDict = dict()
        for newsId in newsIdList:
            newsDict[newsId] = loader.getNews(newsId, corpusTable)
    
    if newsLoaderConfig['get_topic']:
        for newsId, news in newsDict.items():
            news['topic'] = loader.getTopic(newsId, topicIdList)

    print "#news:%d" % (len(newsDict))
    loader.dumpNews(outputJsonFile, newsDict)

