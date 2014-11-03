# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exceptions import DropItem

class NewsCrawlerPipeline(object):
    def __init__(self, db_info):
        self.db_info = db_info

    @classmethod
    def from_crawler(cls, crawler):
        print crawler.spiders.crawler.NewsSpider
        print crawler.parsed_error_log 
        return cls(db_info = crawler.parsed_error_log)
        '''
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )
		'''

    def open_spider(self, spider):
        '''
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        '''
        print 'open_spider'

    def close_spider(self, spider):
        #self.client.close()
        print 'close spider'

    def process_item(self, item, spider):
    	if len(item['title']) != 1:
    		raise DropItem('Not exactly 1 title in, %s' % item['url'])
    	elif len(item['content']) != 1:
    		raise DropItem('Not exactly 1 content in, %s' % item['url'])
    	elif len(item['title'][0].strip()) == 0:
    		raise DropItem('Title is empty in, %s' % item['url'])
    	elif len(item['content'][0].strip()) == 0:
    		raise DropItem('Content is empty in, %s' % item['url'])
    	else:
        	return item
