#!/usr/bin/env python

import sys
import MySQLdb
import json


# filter the news with important keywords
class NewsFilter():
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

        # initialize the connection to database, for insertion
        db2 = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor2 = db2.cursor()
        self.db2 = db2
        self.cursor2 = cursor2

    def contain_keywords(self, news, keywords, min_num):
        title = news['title']
        content = news['content']

        cnt = 0
        for w in keywords:
            cnt += title.count(w)
            cnt += content.count(w)
            if cnt >= min_num:
                return True
        return False

    def exec_select_cmd(self, src_table):
        sql = 'SELECT id, title, content FROM %s' % src_table
        try:
            self.cursor.execute(sql)
        except Exception, e:
            print e

    def fetch_one_news(self):
        try:
            tmp = self.cursor.fetchone()
            if tmp == None:
                return None
            news = dict()
            news['id'] = tmp[0]
            news['title'] = tmp[1]
            news['content'] = tmp[2]
            return news
        except Exception, e:
            print e
            return None
        

    def filter_topic_news(self, config):
        target_table = config['target_table']
        src_table = config['src_table']

        topic_id_list = list()
        keywords_list = list()
        min_f_list = list()
        topic_num = 0
        for topic_config in config['topic_configs']:
            topic_id_list.append(topic_config['id'])
            keywords_list.append(topic_config['keywords'])
            min_f_list.append(topic_config['minimum_frequency'])
            topic_num += 1

        self.exec_select_cmd(src_table)
        topic_news_list = list()
        cnt = 0 
        topic_news_num = 0
        while True:
            news = self.fetch_one_news()
            if news == None:
                break
            for i in range(0, topic_num):
                topic_id = topic_id_list[i]
                keywords = keywords_list[i]
                min_f = min_f_list[i]
                if self.contain_keywords(news, keywords, min_f):
                    topic_news_list.append((topic_id, news['id']))
            cnt += 1
            if cnt % 100 == 0:
                self.insert_data_to_target_table(topic_news_list, target_table)
                topic_news_num += len(topic_news_list)
                topic_news_list = list()
                print 'Filtered News:', cnt, '  #Pairs of topic_news:', topic_news_num
                sys.stdout.flush()
        return 

    def insert_data_to_target_table(self, topic_news_list, target_table):
        for topic_id, news_id in topic_news_list:
            try:
                sql = 'INSERT INTO %s(topic_id, news_id) VALUES' % (target_table)
                self.cursor2.execute(sql + '(%s, %s)', (topic_id, news_id))
                self.db2.commit()
            except Exception, e:
                print '%s' % e
                self.db2.rollback()

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
        print >>sys.stderr, 'Usage:', sys.argv[0], 'topic_json db_info_json'
        exit(-1)

    topic_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]

    with open(topic_json_file, 'r') as f:
        topic_config = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    nf = NewsFilter(db_info) 
    nf.filter_topic_news(topic_config)

