#!/usr/bin/env python

import sys
import MySQLdb
import json
import re

from bs4 import BeautifulSoup

# preprocess all news (removing meanlingless information from news
# and insert into another table)
class NewsPreprocessor():
    defaultColumns = ['title', 'content', 'time', 'url', 'source', 'short_name'] 

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
        
        # initialize the connection to database
        db2 = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor2 = db2.cursor()
        self.db2 = db2
        self.cursor2 = cursor2


    def exec_select_cmd(self, topic_news_table, corpus_table, columns = defaultColumns):
        sql = 'SELECT D.id'
        for c in columns:
            sql = sql + ', D.%s' % (c)
        sql = sql + ''' FROM (SELECT DISTINCT(A.news_id) FROM `%s` as A, `%s` as B where A.news_id = B.id) 
                as C, `%s` as D WHERE C.news_id = D.id''' % (topic_news_table, corpus_table, corpus_table)
        print sql
        try:
            self.cursor.execute(sql)
        except Exception, e:
            print e
            exit(-1)

    def fetch_one_news(self, columns = defaultColumns):
        try:
            tmp = self.cursor.fetchone()
            if tmp == None:
                return None
            else:
                news = dict()
                news['id'] = tmp[0]
                for i, c in enumerate(columns):
                    news[c] = tmp[1+i]
            return news
        except Exception, e:
            print e
            return None

    def preprocess_all_news(self, preprocess_news_config):
        topic_news_table = preprocess_news_config['topic_news_table']
        corpus_table = preprocess_news_config['corpus_table']
        target_table = preprocess_news_config['target_table']
        replace_regex_config = preprocess_news_config['replace_regex_config']
        
        self.exec_select_cmd(topic_news_table, corpus_table)
        while True:
            news = self.fetch_one_news()
            if news == None:
                break
            news = self.preprocess_one_news(news, replace_regex_config)
            self.insert_preprocessed_news(news, target_table) 
    
    def preprocess_one_news(self, news, replace_regex_config):
        for config in replace_regex_config:
            column = config['column']
            if column not in news:
                continue
            print column
            for regex_from, regex_to in config['regex_list']:
                print 'regex_from:', regex_from.encode('utf-8')
                print 'regex_to:', regex_to
                print '--------------original----------------'
                print news[column].encode('utf-8')
                news[column] = re.sub(regex_from, regex_to, news[column], flags=re.UNICODE)
                print '--------------later-------------------'
                print news[column].encode('utf-8')
                sys.stdout.flush()
        
        return news
        
    def insert_preprocessed_news(self, news, table):
        sql = 'INSERT INTO %s(id, title, content, time, url, source, short_name) VALUES' % (table)
        try:
            self.cursor2.execute(sql + '(%s, %s, %s, %s, %s, %s, %s)', (news['id'], news['title'], news['content'], news['time'], news['url'], news['source'], news['short_name']))
            self.db2.commit()
        except Exception, e:
            print e
            self.db2.rollback()


'''
preprocess_news_json = {
    "topic_news_table": ...,
    "corpus_table": ...,
    "replace_regex_config": [ 
     {
        "column": "title",
        "regex_list": [["from1", "to1"], ["from2", "to2"]]
     }, 
     ...
}
news will be preprocessed
'''

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'preprocess_news_json db_info_json'
        exit(-1)

    preprocess_news_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]

    with open(preprocess_news_json_file, 'r') as f:
        preprocess_news_config = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    np = NewsPreprocessor(db_info)
    np.preprocess_all_news(preprocess_news_config)

