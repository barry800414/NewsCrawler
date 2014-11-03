from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from news_crawler.items import NewsItem
import json


class NewsSpider(CrawlSpider):
    name = 'news_crawler'
    allowed_domains = ['udn.com']
    start_urls = ['http://udn.com/NEWS/OPINION/']
    rules = [Rule(LinkExtractor(allow=['.*']), callback='parse_news', follow=False)]
    parsed_error_log = 'parsed_error_log'

    def __init__(self, config_file=None,  *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)
        self.read_config(config_file)
        self.parsed_error_log = '1234dska;dsa'

    def read_config(self, filename):
        pass
        '''
        with open(filename, 'r') as f:
            config = json.load(f)
        print config
        #self.allowed_domains = config['allowed_domains']
        #self.start_urls = config['start_urls']
        '''

    def parse_news(self, response):
        news = NewsItem()
        #print response.url
        news['url'] = response.url
        #print response.xpath("//div[@id='story_title']").extract()
        news['title'] = response.xpath("//div[@id='story_title']").extract()
        #print response.xpath("//div[@id='story']").extract()
        news['content'] = response.xpath("//div[@id='story']").extract()
        return news

    def process_item(self, item, spider):
        print 'test process item'    
