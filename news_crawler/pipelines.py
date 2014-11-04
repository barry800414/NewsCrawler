# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem
#import MySQLdb

class NewsCrawlerPipeline(object):

    def open_spider(self, spider):
        '''
        # initialize the connection to database
        db_info = spider.db_info
        self.db = MySQLdb.connect(db_info['host'], db_info['user'], db_info['password'], port=db_info['port'])
        self.cursor = self.db.cursor()
        '''
        # load history file
        print 'open spider'

    def close_spider(self, spider):
        '''
        self.db.close()
        '''
        print 'close spider'

    def process_item(self, item, spider):
    	if len(item['title']) != 1:
            print 'Not exactly 1 title in, %s' % item['url']
            raise DropItem('Not exactly 1 title in, %s' % item['url'])
    	elif len(item['content']) != 1:
            print 'Not exactly 1 content in, %s' % item['url']
            raise DropItem('Not exactly 1 content in, %s' % item['url'])
    	elif len(item['title'][0].strip()) == 0:
            print 'Title is empty in, %s' % item['url']
            raise DropItem('Title is empty in, %s' % item['url'])
        elif len(item['content'][0].strip()) == 0:
            print 'Content is empty in, %s' % item['url']
            raise DropItem('Content is empty in, %s' % item['url'])
    	else:
            return item
