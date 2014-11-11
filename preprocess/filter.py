#!/usr/bin/env python

import sys
import MySQLdb

class NewsFilter():
    def __init__(topic_config, news_config, db_config):
        self.topic_config = topic_config
        self.news_config = news_config
        self.db_config = db_config

        self.connect_to_db()

    def connect_to_db(self):
        # initialize the connection to database
        db_info = db_config['db_info']
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

    def exec_select_cmd(self):
        sql = 'SELECT id, title, content FROM %s' % src_table
        try:
            self.cursor.execute(sql)
        except:
            print e

    def fetch_one_news(self):
        try:
            tmp = self.cursor.fetchone()
            news = dict()
            news['id'] = tmp[0]
            news['title'] = tmp[1]
            news['content'] = tmp[2]
            return news
        except:
            print e
            return None
        

    def filter_one_topic_news(self, topic):
        target_table = topic['target_table']
        src_tables = topic['src_tables']
        keywords = topic['keywords']
        max_news = topic['max_filtered_news']

        news_list = list()
        for src_table in src_tables:
            self.exec_select_cmd(src_table)
            selected_news = list()
            while True:
                news = self.cursor.fetchone()
                if news == None:
                    break
                if contain_keywords(news, keywords):
                    news_list.append(news['id'])
                    if len(news_list) >= max_news:
                        break
            if len(news_list) >= max_news:
                break
        
        self.insert_data_to_target_table(topic['id'], news_list, target_table)
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

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'topic_json db_config_json'
        exit(-1)

    topic_json_file = sys.argv[1]
    news_website_json_file = sys.argv[2]

    with open(topic_json_file, 'r') as f:
        topic_config = json.load(f)

    nf = NewsFilter(topic_config, db_config) 
    nf.filter_news()

