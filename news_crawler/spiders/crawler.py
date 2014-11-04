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
        NewsSpider.error_log = config['error_log']
        self.rules = [Rule(LinkExtractor(allow=['.*'], deny_domains=config['deny_domains']), callback='parse_news', follow=True)]

    def parse_news(self, response):
        news = NewsItem()
        #print response.url
        news['url'] = response.url
        news['title'] = response.xpath(self.config['xpath']['title']).extract()
        
        #news['title'] = response.css('#story_title::text').extract()
        '''      
        print news['title']
        if len(news['title']) == 1:
            print news['title'][0].encode('utf-8')
        '''
        news['content'] = response.xpath(self.config['xpath']['content']).extract()

        #news['content'] = response.css('#story p').extract()
        '''
        print news['content']
        if len(news['content']) == 1:
            print news['content'][0].encode('utf-8')
        '''
        return news
