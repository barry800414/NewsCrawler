#!/usr/bin/env python

import sys
import MySQLdb
import json

class NewsFilter():
    def __init__(self, topic_config, db_info):
        self.topic_config = topic_config

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

    def contain_keywords(self, news, keywords):
        title = news['title']
        content = news['content']

        for w in keywords:
            if title.find(w) != -1:
                return True
            if content.find(w) != -1:
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
        

    def filter_one_topic_news(self, topic):
        topic_id = topic['id']
        target_table = topic['target_table']
        src_table = topic['src_table']
        keywords = topic['keywords']
        max_news = topic['max_filtered_news']

        news_list = list()
        self.exec_select_cmd(src_table)
        selected_news = list()
        while True:
            news = self.fetch_one_news()
            if news == None:
                break
            if self.contain_keywords(news, keywords):
                news_list.append(news['id'])
                if len(news_list) >= max_news and max_news != -1:
                    break
            if len(news_list) >= max_news and max_news != -1:
                break

        self.insert_data_to_target_table(topic_id, news_list, target_table)
        return 

    def filter_news(self):
        for topic in self.topic_config:
            self.filter_one_topic_news(topic)
        return

    def insert_data_to_target_table(self, topic_id, news_list, target_table):
        for news_id in news_list:
            try:
                sql = 'INSERT INTO %s(topic_id, news_id) VALUES' % (target_table)
                self.cursor.execute(sql + '(%s, %s)', (topic_id, news_id))
                self.db.commit()
            except:
                print '%s' % e
                self.db.rollback()

'''
topic_json = [ topic1, topic2 ...]
topic = {
    "id": ...,
    "target_table": ...,
    "src_table": ...,
    "keywords": [...],
    "max_filtered_news": ... (-1 means no limit)
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

    nf = NewsFilter(topic_config, db_info) 
    nf.filter_news()

