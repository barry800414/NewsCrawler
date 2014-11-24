# coding=utf-8
import urlparse

url = "HTTP://www.Python.org/docs/?ada=dasd#dsa"

print urlparse.urldefrag(url)


from scrapy.selector import Selector
from scrapy.http import HtmlResponse

content = '<td class="story_title"><div style="float:left">wait 13 year</div><div id=bq  style="float:right">測試  測試<IFRAME height=25 src="/2010/AD/CAMPUS_BQ.html" frameBorder=0 width=150 scrolling=no></IFRAME></div></td>'


result =  Selector(text=content).xpath("//td[@class='story_title']/div[@style='float:right']/text()").extract()

for i,c in enumerate(result):
    print '%d-th:' % (i+1)
    print c.encode('utf-8')

