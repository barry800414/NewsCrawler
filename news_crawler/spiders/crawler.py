from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor

from news_crawler.items import NewsItem
import json
import urlparse
import codecs

class NewsSpider(CrawlSpider):
    name = 'news_crawler'

    def __init__(self, config_file=None,  *args, **kwargs):
        

        # read in configuration file
        self.read_config(config_file)
        super(NewsSpider, self).__init__(*args, **kwargs)
        
    def read_config(self, filename):
        with open(filename, 'r') as f:
            config = json.load(f)
        #config['src_name'] = config['src_name'].encode('utf-8')
        #config['db_info']['table'] = config['db_info']['table'].encode('utf-8')
        self.config = config
        self.allowed_domains = config['allowed_domains']
        self.start_urls = config['start_urls']
        self.rules = [Rule(LinkExtractor(allow=['.*'], deny_domains=config['deny_domains']), callback='parse_news', follow=True)]

    def parse_news(self, response):
        news = NewsItem()
        #print response.url
        news['url'] = response.url

        # try different xpath
        for field in self.config['xpath'].keys():
            news[field] = None
            for x in self.config['xpath'][field]: 
                tmp = response.xpath(x['xpath']).extract() 
                #if field == u'time':
                #    print tmp
                if len(tmp) == x['expect']:
                    if len(tmp[x['index']].strip()) != 0:
                        news[field] = tmp[x['index']].strip()
                        break
        '''
        if news['title'] != None:
            print 'title:', news['title'].encode('utf-8')
        else:
            print 'title: None'
        '''

        return news
