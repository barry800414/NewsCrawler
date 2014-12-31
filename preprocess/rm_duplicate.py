#!/usr/bin/env python

import sys
import MySQLdb
import json
import math

# remove duplicated news under certain topic
# all pairs compare
class DuplicateRemover():
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

    def fetch_all_news_for_one_topic(self, topic_id):
        news_list = list()
        sql = '''SELECT B.id, B.title, B.content, B.url
                 FROM %s as A, %s as B ''' % (self.topic_news_table, 
                         self.corpus_table)
        try:
            self.cursor.execute(sql + 'WHERE A.news_id = B.id AND A.topic_id = %s', (topic_id,))
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    news = dict()
                    news['id'] = tmp[0]
                    news['title'] = tmp[1]
                    news['content'] = tmp[2]
                    news['url'] = tmp[3]
                    news_list.append(news)
        except Exception, e:
            print e
        return news_list

    def remove_duplicated_news_for_one_topic(self, topic_config):
        topic_id = topic_config['id']

        news_list = self.fetch_all_news_for_one_topic(topic_id)
        
        # calculating term frequency
        for news in news_list:
            news['title_tf'] = self.get_term_frequency(news['title'])
            news['content_tf'] = self.get_term_frequency(news['content'])

        # finding duplicated news
        to_remove = set()
        total_task = (len(news_list) * (len(news_list) - 1)) / 2
        cnt = 0
        for i, n1 in enumerate(news_list):
            for j in range(i+1, len(news_list)):
                n2 = news_list[j]
                if n2['id'] in to_remove:
                    continue
                if self.is_same_news(n1, n2):
                    to_remove.add(n2['id'])
                cnt = cnt + 1
                if cnt % 1000 == 0:
                    print >>sys.stderr, 'Progress(%d/%d)' % (cnt, total_task)
        
        # remove duplicated news
        self.remove_data_from_table(self.topic_news_table, topic_id, to_remove)   

    def get_term_frequency(self, string):
        tf = dict()
        for c in string:
            if c not in tf:
                tf[c] = 1
            else:
                tf[c] += 1
        return tf
    
    def is_same_news(self, news1, news2):
        title_sim = self.cos_sim(news1['title_tf'], news2['title_tf'])
        content_sim = self.cos_sim(news1['content_tf'], news2['content_tf'])
        if title_sim > 0.5 and content_sim > 0.9:
            
            print '---------------------------------------'
            print 'Title Sim:' + str(title_sim)
            print 'Content Sim:' + str(content_sim)
            print 'NewsID1:' + news1['id']
            print 'NewsID2:' + news2['id']
            print 'Title1:' + news1['title'].encode('utf-8')
            print 'Title2:' + news2['title'].encode('utf-8')
            print 'Url1:' + news1['url']
            print 'Url2:' + news2['url']
            sys.stdout.flush()
            '''
            print 'Content1:' + news1['content'].encode('utf-8')
            print 'Content2:' + news2['content'].encode('utf-8')
            for key,value in news1['content_tf'].items():
                print key.encode('utf-8') + ':' + str(value)
            for key,value in news2['content_tf'].items():
                print key.encode('utf-8') + ':' + str(value)
            '''
            return True
        else:
            return False

    def cos_sim(self, tf1, tf2):
        value = 0.0
        common_term = set(tf1.keys()) & set(tf2.keys())
        for t in common_term:
            value += tf1[t] * tf2[t] 
        norm = 0.0
        for v in tf1.values():
            norm += v * v
        value = value / math.sqrt(norm)
        norm = 0.0
        for v in tf2.values():
            norm += v * v
        value = value / math.sqrt(norm)
        return value

    def remove_duplicated_news(self, config):
        self.topic_news_table = config['target_table']
        self.corpus_table = config['src_table']
        for topic_config in config['topic_configs']:
            self.remove_duplicated_news_for_one_topic(topic_config)
        return

    def remove_data_from_table(self, table_name, topic_id, news_id_set):
        for news_id in news_id_set:
            try:
                sql = 'DELETE FROM `%s` WHERE ' % table_name
                self.cursor.execute(sql + " topic_id=%s AND news_id=%s", (topic_id, news_id))
                self.db.commit()
            except Exception, e:
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

    dr = DuplicateRemover(db_info) 
    dr.remove_duplicated_news(topic_config)

