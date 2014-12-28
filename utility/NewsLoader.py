#!/usr/bin/env python

import sys
import MySQLdb
import json

class NewsLoader():
    def __init__(self, db_info, table_info=None):
        self.connectToDB(db_info)
        if table_info != None:
            self.topic_news_table = table_info['topic_news_table']
            self.topic_table = table_info['topic_table']
        
    def connectToDB(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def __convert_to_sql(self, column, prefix=None):
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
    def getNews(self, newsId, table, newsColumns = ['title', 'content']):
        sql = 'SELECT %s FROM %s' % (self.__convert_to_sql(newsColumns), table)
        try:
            self.cursor.execute(sql + ' WHERE id=%s', (newsId, ))
            tmp = self.cursor.fetchone()
            if tmp == None:
                return None
            else:
                news = dict()
                news['id'] = newsId
                for i, c in enumerate(newsColumns):
                    news[c] = tmp[i]
                return news
        except Exception, e:
            print e
            return None

    # get news from given topic and given table
    def getNewsByTopic(self, topicId, limitNum, table, newsColumns = ['title', 'content']):
        sql = '''
            SELECT A.news_id, %s FROM %s as A, %s as B, %s as C
            WHERE A.topic_id = B.id AND A.news_id = C.id
        ''' % (self.__convert_to_sql(news_colunms, 'C'), 
                self.topic_news_table, self.topic_table, table)
        
        try:
            newsList = list()
            #execute the sql 
            if limitNum == -1:
                self.cursor.execute(sql + ' AND A.topic_id = %d', (topicId, ))
            else:
                self.cursor.execute(sql + ' AND A.topic_id = %d LIMIT 0, %d', (topicId, limitNum))
            #fetch rows
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    news = dict()
                    news['id'] = tmp[0]
                    for i, c in enumerate(newsColumns):
                        news[c] = tmp[i+1]
                    newsList.append(r)
            return newsList
        except Exception, e:
            print e
            return None
        

    def dumpNews(self, filename, newsList):
        with open(filename, 'w') as f:
            json.dump(newsList, f)


'''
news_loader_json = {
    "topic_news_table": "topic_news",
    "topic_table": "topic",
    "corpus_table": "merge",
    "topic_id": 1,
    "news_id": ["setn0000001"], 
    "query_type" : "topic/news",
    "limit_num": 300
}
'''

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'news_loader_json db_info_json output_json_file'
        exit(-1)

    news_loader_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]
    output_json_file = sys.argv[3]

    with open(news_loader_json_file, 'r') as f:
        news_loader_config = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    loader = NewsLoader(db_info)
    if news_loader_json['query_type'] == 'topic':
        topicId = news_loader_json['topic_id']
        limitNum = news_loader_json['limit_num']
        corpusTable = news_loader_json['corpus_table']
        newsList = loader.getNewsByTopic(topicId, limitNum, corpusTable)

    elif news_loader_json['query_type'] == 'news':
        newsIdList = news_loader_json['news_id']
        corpusTable = news_loader_json['corpus_table']
        newsList = list()
        for newsId in newsIdList:
            newsList.append(loader.getNews(self, newsId, corpusTable))

    loader.dumpNews(output_json_file, newsList)
