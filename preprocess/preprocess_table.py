#!/usr/bin/env python

import sys
import MySQLdb
import json
import re

from bs4 import BeautifulSoup

# removing html tags of all news in one table
class TablePreprocessor():
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

        # for insertion
        db2 = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor2 = db2.cursor()
        self.db2 = db2
        self.cursor2 = cursor2

    def execute_select_cmd(self, table, columns = defaultColumns):
        sql = 'SELECT id'
        for c in columns:
            sql = sql + ', %s' % (c)
        sql = sql + ' FROM %s' % (table)
        print sql
        try:
            self.cursor.execute(sql)
        except Exception, e:
            print e
            exit(-1)
        return

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

    def preprocess_one_table(self, config):
        src_table = config['src_table']
        target_table = config['target_table']
                
        # for each news: 1. check remove or not  2.cleanning content 
        print 'Now preprocessing: %s' % (src_table)
        self.execute_select_cmd(src_table)
        cnt = 0 
        while True:
            cnt += 1
            if cnt % 100 == 0:
                print cnt
            
            news = self.fetch_one_news()
            if news == None:
                break

            # to check whether the news should be removed
            to_remove = False
            for remove_regex in config['remove_regex_config']:
                if to_remove:
                    break
                column = remove_regex['column'] #e.g. title, content
                regex_list = remove_regex['regex_list']
                for regex in regex_list: # match one of regex => remove
                    r = re.match(regex, news[column])
                    if r != None:
                        to_remove = True
                        break
            if to_remove:
                print 'remove: ', news['id'], news['title'].encode('utf-8')
                continue

            else: # pass the examination of removing regex, do preproccessing
                news = self.preprocess_one_news(news, config['preprocess_config'])
                if self.should_drop(news):
                    print 'drop: ', news['id'], news['title'].encode('utf-8')
                else:
                    self.insert_news(news, target_table)

            # debug:
            #print news['content']

    def preprocess_one_news(self, news, preprocess_config):
        for config in preprocess_config:
            column = config['column']
            method = config['method']
            if method == 'bs4_get_text':
                soup = BeautifulSoup(news[column])
                news[column] = soup.get_text().strip()
        return news

    def should_drop(self, news):
        if news['title'].strip() == '':
            return True
        if news['content'].strip() == '':
            return True
        return False

    def preprocess_tables(self, preprocess_table_config):
        for config in preprocess_table_config:
            self.preprocess_one_table(config)

    def insert_news(self, news, table):
        sql = 'INSERT INTO %s(id, title, content, time, url, source, short_name) VALUES' % (table)
        try:
            self.cursor2.execute(sql + '(%s, %s, %s, %s, %s, %s, %s)', (news['id'], news['title'], news['content'], news['time'], news['url'], news['source'], news['short_name']))
            self.db2.commit()
        except Exception, e:
            print e
            self.db2.rollback()

'''
preprocess_json = [ config1, config2, .. ]
config = {
    "src_table": ...,
    "target_table": ...,
    "remove_regex_config": [ 
     {
        "column": "title",
        "regex_list": ["regex1", "regex2" ...]
     }, ...
     ],
     "preprocess_config": [
        {
            "column": "title", 
            "method": "bs4_get_text"
        }, ...
     ]
}
news will be removed if match any one of regex
news will be preprocessed
'''

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'preprocess_table_json db_info_json'
        exit(-1)

    preprocess_table_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]

    with open(preprocess_table_json_file, 'r') as f:
        preprocess_table_config = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    tp = TablePreprocessor(db_info) 
    tp.preprocess_tables(preprocess_table_config)

