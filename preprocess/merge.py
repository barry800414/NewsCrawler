#!/usr/bin/env python

import sys
import MySQLdb
import json

# merge all news (after removing html tags) to one table
class Merger():
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


    def merge_news_tables(self, table_info):
        target_table = table_info['target_table']
        src_table_config = table_info['src_table_config']
        for config in src_table_config:
            src_table = config['table']
            priority = config['priority']
            sql = '''INSERT INTO `%s`(id, title, content, time, url, source, short_name)
                    SELECT concat('%02d_', short_name, '_', lpad(id, 8, '00000000')) as id, title, 
                    content, time, url, source, short_name FROM `%s`''' % (target_table, priority, src_table)
            print sql
            try:
                self.cursor.execute(sql) 
                self.db.commit()
            except Exception, e:
                print e
                self.rollback()
        
    def merge_news_tables_2(self, table_info):
    
        target_table = table_info['target_table']
        src_table = table_info['src_table']
        for table in src_table:
            news_list = list()
            sql = 'SELECT id, title, content, time, url, source, short_name FROM %s' % table
            try:
                self.cursor.execute(sql) 
                while True:
                    tmp = self.cursor.fetchone()
                    if tmp == None:
                        break
                    news = dict()
                    news['title'] = tmp[1]
                    news['content'] = tmp[2]
                    news['time'] = tmp[3]
                    news['url'] = tmp[4]
                    news['source'] = tmp[5]
                    news['short_name'] = tmp[6] 
                    news['id'] = str(news['short_name']) + '_' + str(tmp[0])
                    news_list.append(news)
            except Exception, e:
                print e
            
            try:
                sql = 'INSERT INTO %s(id, title, content, time, url, source, short_name) VALUES' % (target_table)
                print news_list[0]
                for news in news_list:
                    self.cursor.execute(sql + '(%s, %s, %s, %s, %s, %s, %s)', (news['id'], news['title'], news['content'],
                        news['time'], news['url'], news['source'], news['short_name']))
                    self.db.commit()
            except Exception, e:
                print '%s' % e
                self.db.rollback()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'table_info_json db_info_json'
        exit(-1)

    table_info_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]

    with open(table_info_json_file, 'r') as f:
        table_info = json.load(f)

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    m = Merger(db_info)
    m.merge_news_tables(table_info)


