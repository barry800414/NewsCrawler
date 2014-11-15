#!/usr/bin/env python

import sys
import MySQLdb
import json

class TopicInserter():
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

    def insert_topics(self):
        for topic in self.topic_config:
            keywords = '';
            for w in topic['keywords']:
                keywords = keywords + w + ','

            try:
                sql = 'INSERT INTO topic(id, name, keywords) VALUES';
                self.cursor.execute(sql + '(%s, %s, %s)', (topic['id'], topic['topic'],keywords))
                self.db.commit()
            except Exception, e:
                print '%s' % e
                self.db.rollback()
            
            for s in topic['statements']:
                try:
                    sql = 'INSERT INTO statement(content, topic_id) VALUES'
                    self.cursor.execute(sql + '(%s, %s)', (s, topic['id']))
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

    ti = TopicInserter(topic_config, db_info) 
    ti.insert_topics()

