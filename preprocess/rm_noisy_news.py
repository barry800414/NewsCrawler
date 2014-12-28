#!/usr/bin/env python

import sys
import MySQLdb
import json
import re

#depricated
class NoisyNewsRemover():
    def __init__(self, toremove_news_config, db_info):
        self.toremove_news_config = toremove_news_config
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

    def execute_select_cmd(self, table):
        sql = 'SELECT id, title, content from `%s`' % (table)
        try:
            self.cursor.execute(sql)
        except Exception, e:
            exit(-1)
        return

    def fetch_one_news(self):
        try:
            tmp = self.cursor.fetchone()
            if tmp == None:
                return None
            else:
                news = dict()
                news['id'] = tmp[0]
                news['title'] = tmp[1]
                news['content'] = tmp[2]
                return news
        except Exception, e:
            print e
            return None

    def clean_one_table(self, config):
        table = config['table']
        self.execute_select_cmd(table)
        
        # find the news to remove
        to_remove_set = set()
        while True:
            news = self.fetch_one_news()
            if news == None:
                break
            to_remove = False
            for title_reg in config['title_regex_list']:
                r = re.match(title_reg, news['title'])
                if r != None:
                    print news['id'], news['title'].encode('utf-8')
                    to_remove_set.add(news['id'])
                    to_remove = True
                    break
            if to_remove:
                continue
            for content_reg in config['content_regex_list']:
                r = re.match(content_reg, news['content'])
                if r != None:
                    print news['id'], news['content'].encode('utf-8')
                    to_remove_set.add(news['id'])
                    to_remove = True
                    break
        # remove the news
        self.remove_news_from_table(table, to_remove_set)

    def clean_tables(self):
        for config in self.toremove_news_config:
            self.clean_one_table(config)

    def remove_news_from_table(self, table, news_id_set):
        for news_id in news_id_set:
            try:
                sql = 'DELETE FROM `%s` WHERE ' % table
                self.cursor.execute(sql + " id=%s", (news_id, ))
                self.db.commit()
            except Exception, e:
                print '%s' % e
                self.db.rollback()

'''
toremove_news_json = [ config1, config2, .. ]
config = {
    "table": ...,
    "title_regex_list": [regex1, regex2, ...],  
    "content_regex_list": [regex1, regex2, ...]
}
news will be removed if match any one of regex
'''


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'toremove_news_json db_info_json'
        exit(-1)

    toremove_news_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]

    with open(toremove_news_json_file, 'r') as f:
        toremove_news_config = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    dr = NoisyNewsRemover(toremove_news_config, db_info) 
    dr.clean_tables()

