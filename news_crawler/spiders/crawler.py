from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor

from news_crawler.items import NewsItem
import json
import urlparse


class NewsSpider(CrawlSpider):
    name = 'news_crawler'
    allowed_domains = ['udn.com']
    start_urls = ['http://udn.com/NEWS/OPINION/']
    rules = [Rule(LinkExtractor(allow=['.*']), callback='parse_news', follow=False)]

    def __init__(self, config_file=None,  *args, **kwargs):
        super(NewsSpider, self).__init__(*args, **kwargs)

        # read in configuration file
        self.read_config(config_file)
        
    def read_config(self, filename):
        with open(filename, 'r') as f:
            config = json.load(f)
        self.config = config
        NewsSpider.allowed_domains = config['allowed_domains']
        NewsSpider.start_urls = config['start_urls']
        NewsSpider.error_log = config['error_log']

    def parse_news(self, response):
        news = NewsItem()
        #print response.url
        news['url'] = response.url
        #print response.xpath("//div[@id='story_title']").extract()
        news['title'] = response.xpath("//div[@id='story_title']/text()").extract()
        print news['title']
        if len(news['title']) == 1:
            print news['title'][0].encode('utf-8')
        #print response.xpath("//div[@id='story']").extract()
        news['content'] = response.xpath("string(//div[@id='story'])").extract()
        print news['content']
        if len(news['content']) == 1:
            print news['content'][0].encode('utf-8')

        return news
