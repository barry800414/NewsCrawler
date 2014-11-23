from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.contrib.linkextractors.lxmlhtml import LxmlLinkExtractor

from news_crawler.items import NewsItem
import json
import urlparse
import codecs

class NewsSpider(CrawlSpider):
    name = 'news_crawler'

    def __init__(self, config_file=None, debug=False, single_url='',*args, **kwargs):
        # check whether debug mode is on or not
        self.set_debug_mode(debug)

        # if single_url is setted, we only craw the data from the url
        # Besides, we will output the item at the end of process
        self.set_single_url(single_url)

        # read in configuration file
        self.read_config(config_file)
        super(NewsSpider, self).__init__(*args, **kwargs)
        
    def set_debug_mode(self, debug):
        if debug == 1 or debug == '1' or debug == 'True': 
            self.debug=True
        else:
            self.debug=False

    def set_single_url(self, single_url):
        if len(single_url.strip()) != 0:
            self.single_url = single_url.strip()
        else:
            self.single_url = None

    def read_config(self, filename):
        with open(filename, 'r') as f:
            config = json.load(f)
        self.config = config
        self.allowed_domains = config['allowed_domains']

        # If we don't give crawler a single url request, we crawl all webpages in this website
        if self.single_url == None:
            self.start_urls = config['start_urls']
            allow_config = '.*' #default: all links
            if 'allow' in config and len(config['allow']) > 0:
                allow_config = config['allow']
            self.rules = [Rule(LinkExtractor(allow=allow_config, deny=config['deny'], 
                deny_domains=config['deny_domains']), callback='parse_news', follow=True)]
        else: # if single_url is setted, we only craw the data from the url
            self.start_urls = [self.single_url]
            self.rules = [Rule(LinkExtractor(allow=[self.single_url]), callback='parse_news', follow=False)]

    def parse_news(self, response):
        news = NewsItem()
        #print response.url
        news['url'] = response.url

        # try different xpath
        if self.debug:
            print ''
        for field in self.config['xpath'].keys():
            news[field] = None
            for x in self.config['xpath'][field]: 
                tmp = response.xpath(x['xpath']).extract() 
                
                # debug mode
                if self.debug:
                    self.print_parsed_result(field, x['xpath'], tmp)
            
                # to merge all matched results 
                if x['expect'] == -1 and x['index'] == 'merge_all':
                    news[field] = self.merge_result(tmp)
                    if news[field] != None:
                        break

                # extract only one result
                else:
                    if len(tmp) == x['expect']: 
                        if len(tmp[x['index']].strip()) != 0:
                            news[field] = tmp[x['index']].strip()
                            break
        return news  #then the object will fed into pipeline

    def merge_result(self, parsed_result):
        if len(parsed_result) == 0:
            return None
        merge = u''
        for s in parsed_result:
            merge += s.strip() + u'\n'           
        if len(merge.strip()) == 0:
            return None
        else:
            return merge.strip()

    def print_parsed_result(self, field, xpath, parsed_result):
        print field, '     ', xpath, '     ', parsed_result
        for s in parsed_result:
            print s.encode('utf-8')


# for disabling dropping messages
from scrapy import log
from scrapy import logformatter

class PoliteLogFormatter(logformatter.LogFormatter):
    def dropped(self, item, exception, response, spider):
        return {
            'level': log.DEBUG,
            'format': logformatter.DROPPEDFMT,
            'exception': exception,
            'item': item,
    }
