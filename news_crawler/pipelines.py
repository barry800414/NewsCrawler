# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import MySQLdb
import sys
import re

class NewsCrawlerPipeline(object):

    def open_spider(self, spider):
        self.db_table = spider.config['db_info']['table']
        self.src_name = spider.config['src_name']
        
        # if url match the regex, then do not ouput dropped message
        self.ignore_urls_regex = spider.config['ignore_urls_regex']

        # initialize the connection to database
        db_info = spider.config['db_info']
        self.db = MySQLdb.connect(db_info['host'], db_info['user'], 
                db_info['password'], db_info['database'], 
                port=db_info['port'], charset='utf8', 
                init_command='SET NAMES UTF8')
        self.cursor = self.db.cursor()
        # load history file
        print 'open spider'

    def close_spider(self, spider):
        self.db.close()
        print 'close spider'

    def process_item(self, item, spider):
        if spider.single_url != None:
            self.print_news(item, sys.stderr)
        
        to_drop = False
        lack_field = None
        for field in item.keys():
            if field == 'url':
                continue
            if item[field] == None:
                to_drop = True
                lack_field = field

    	if to_drop:
            if not self.should_ignore(item):
                self.print_drop_message(lack_field, item['url'])
            raise DropItem('Can not find %s in %s' % (lack_field, item['url']))
        else:
            # pass the basic evaluation, then preprocess the news content in details
            item = self.preprocess_news(item)
            
            # insert into database 
            self.insert_news(item)

            return item

    def preprocess_news(self, news):
        # more detailed preproces
        return news

    def should_ignore(self, news):
        for regex in self.ignore_urls_regex:
            if re.match(regex, news['url']) != None:
                return True
        return False

    def insert_news(self, news):
        sql = u"INSERT INTO %s(title, content, time, url, source) VALUES " % self.db_table
        #print sql.encode('utf-8')
        try:
            self.cursor.execute(sql + u"(%s, %s, %s, %s, %s)",
                    (news['title'], news['content'], news['time'], 
                        news['url'], self.src_name))
            self.db.commit()
        except Exception, e:
            print '%s' % e
            self.db.rollback()
    
    def print_drop_message(self, field, url):
        print 'Can not find %s in %s' % (field, url)
        print >>sys.stderr, 'Can not find %s in %s' % (field, url)
        sys.stdout.flush()

    def print_news(self, item, fp):
        print >>fp, 'Final Parsed Result:'
        print >>fp, 'Title:', item['title']
        print >>fp, 'Content:', item['content']
        print >>fp, 'Time:', item['time']
        print >>fp, 'Url:', item['url']
