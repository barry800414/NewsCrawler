#!/usr/bin/env python

import sys
import MySQLdb
import json

# this procedure is for moving proper amount of news under
# each topic for annotation
# 2014/12/28

class TopicNewsMover():
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

    def move_one_topic_news(self, config):
        src_table = config['src_table']
        target_table = config['target_table']
        topic_id = config['topic_id']
        order_by = config['order_by']
        range = config['range']  # 2 integers(limit a, b)
        if range[0] == -1 or range[1] == -1:
            return 

        sql = '''INSERT INTO `%s`(id, topic_id, news_id) 
                 SELECT id, topic_id, news_id FROM `%s` WHERE topic_id=%d ORDER BY %s 
                    LIMIT %d,%d''' %(target_table, src_table, topic_id, order_by, range[0], range[1])
        print sql
        try:
            self.cursor.execute(sql) 
            self.db.commit()
        except Exception, e:
            print e
            self.db.rollback()
    
    def move_all_topic_news(self, all_config):
        for config in all_config:
            self.move_one_topic_news(config)

'''
move_topic_news_config :[ config1, config2 ... ]
config:{
    "src_table": "topic_news",
    "target_table": "topic_news_new",
    "topic_id": 1,
    "order_by": "news_id",
    "range": [0, 99] (1-th to 100-th)
}
'''


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'move_topic_news_json db_info_json'
        exit(-1)

    move_topic_news_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]

    with open(move_topic_news_json_file, 'r') as f:
        move_topic_news_config = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    m = TopicNewsMover(db_info)
    m.move_all_topic_news(move_topic_news_config)


