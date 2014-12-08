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
            print 'debug mode'
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
            print self.single_url
            allow_url = self.single_url.replace('?', '\\?')
            allow_url = allow_url.replace('.', '\\.')
            allow_url = allow_url.replace('=', '\\=')
            allow_url = allow_url.replace('&','\\&')
            allow_url = allow_url.replace(':', '\\:')
            allow_url = allow_url.replace('/', '\\/')
            #allow_url = allow_url.replace('_', '\\_')
            print allow_url
            self.rules = [Rule(LinkExtractor(allow=[allow_url]), callback='parse_news', follow=False)]

    def parse_news(self, response):
        news = NewsItem()
        #print response.url
        news['url'] = response.url
        #print response.header
        #print response.status

        # try different xpath
        if self.debug:
            print '=================================================='
        for field in self.config['xpath'].keys():
            news[field] = None
            for x in self.config['xpath'][field]: 
                parsed_results = response.xpath(x['xpath']).extract() 
                
                # if debug mode, print out debug messages
                if self.debug:
                    self.print_parsed_results(field, x['xpath'], parsed_results)
                # if there are not only one content (e.g. parsed_results = ['aaa', 'bbb', ...])
                if x['expect'] == -1:
                    # merge all of them
                    if x['index'] == 'merge_all':
                        news[field] = self.merge_results(parsed_results, sep=u'\n')
                    elif type(x['index']) is list:
                        news[field] = self.merge_some_of_results(parsed_results, x['index'], sep=u'\n')
                    elif type(x['index']) is int:
                        news[field] = self.get_one_of_results(parsed_results, x['index'])
                    elif type(x['index']) is str or type(x['index']) is unicode:
                        news[field] = self.merge_some_of_results_by_index_str(parsed_results, x['index'], sep='\n')
                  
                    if news[field] != None:
                        break
                
                # if there should be certain contents 
                # (e.g. x['expect'] = 3, parsed_results = ['a', 'b', 'c'])
                else:
                    if len(parsed_results) == x['expect']: 
                        news[field] = self.get_one_of_results(parsed_results, x['index'])
                        break

        return news  #then the object will fed into pipeline

    # merge all of them into one string 
    def merge_results(self, parsed_results, sep=''):
        if len(parsed_results) == 0:
            return None
        merge = u''
        for s in parsed_results:
            merge += s.strip() + sep
        merge = merge.strip()

        if len(merge) == 0:
            return None
        else:
            return merge

    # merge some of them into one string
    def merge_some_of_results(self, parsed_results, index_list, sep=''):
        if parsed_results == None:
            return None

        merge = u''
        for index in index_list:
            r = self.get_one_of_results(parsed_results, index)
            if r != None:
                merge += r + sep
        merge = merge.strip()
        if len(merge) == 0:
            return None
        else:
            return merge
    
    # index_str: "2:-1" means 3rd element to (last-1)-th element 
    def merge_some_of_results_by_index_str(self, parsed_results, index_str, sep=''):
        if len(parsed_results) == 0:
            return None
        indexes = index_str.split(':')
        start = None
        end = None
        assert len(indexes) == 2
        if len(indexes[0].strip()) != 0:
            start = int(indexes[0].strip())
        if len(indexes[1].strip()) != 0:
            end = int(indexes[1].strip())
    
        if start == None:
            if end == None:
                pass
            else:
                parsed_results = parsed_results[:end]
        else:
            if end == None:
                parsed_results = parsed_results[start:]
            else:
                parsed_results = parsed_results[start:end]
        

        return self.merge_results(parsed_results, sep = u'\n')
    

    # get one of them
    def get_one_of_results(self, parsed_results, index):
        if parsed_results == None:
            return None

        num = len(parsed_results)
        if self.is_valid_index(num, index):
            r = parsed_results[index].strip()
            if len(r) == 0:
                return None
            else:
                return r
        else:
            return None
    
    def is_valid_index(self,arr_length, index):
        if (index >= 0 and index < arr_length) or (index < 0 and index >= (-1*arr_length)):
            return True
        else:
            return False


    def print_parsed_results(self, field, xpath, parsed_results):
        print field, '     ', xpath, '     ', parsed_results
        for s in parsed_results:
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
