# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
import MySQLdb
import sys

class NewsCrawlerPipeline(object):

    def open_spider(self, spider):
        self.db_table = spider.config['db_info']['table']
        self.src_name = spider.config['src_name']
        self.encoding = spider.config['encoding']

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
        if item['title'] == None:
            print 'Can not find title in %s' % item['url']
            sys.stdout.flush()
            raise DropItem('Can not find title in %s' % item['url'])
        #elif len(item['title'].strip()) == 0:
        #    print 'Can not find title in %s' % item['url']
        #    sys.stdout.flush()
        #    raise DropItem('Can not find title in %s' % item['url'])
        elif item['content'] == None:
            print 'Can not find title in %s' % item['url']
            sys.stdout.flush()
            raise DropItem('Can not find content in %s' % item['url'])
        #elif len(item['content'].strip()) == 0:
        #    print 'Can not find title in %s' % item['url']
        #    sys.stdout.flush()
        #    raise DropItem('Can not find content in %s' % item['url'])
        elif item['time'] == None:
            print 'Can not find time in %s' % item['url']
            sys.stdout.flush()
            raise DropItem('Can not find time in %s' % item['url'])
        #elif len(item['time'].strip()) == 0:
        #    print 'Can not find time in %s' % item['url']
        #    sys.stdout.flush()
        #    raise DropItem('Can not find time in %s' % item['url'])
    	else:
            # pass the basic evaluation, then preprocess the news content in details
            item = self.preprocess_news(item)
            
            # insert into database 
            self.insert_news(item)

            return item

    def preprocess_news(self, news):
        # more detailed preproces
        return news

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
    
    
