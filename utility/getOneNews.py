#!/usr/bin/env python

import sys
import MySQLdb
import json
import re

from NewsLoader import NewsLoader

'''
news_loader_json = {
    "topic_news_table": "topic_news",
    "topic_table": "topic",
    "corpus_table": "merge",
    "topic_id": 1,
    "news_id": ["setn0000001"], 
    "query_type" : "topic/news",
    "limit_num": 300
}
'''

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'db_info_json news_id'
        exit(-1)

    db_info_json_file = sys.argv[1]
    news_id = sys.argv[2]

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    loader = NewsLoader(db_info)
    news = loader.getNews(news_id, 'merge')
    
    for c in news['content']:
        print c,':',ord(c), 

    content = re.sub(u'[\u0009\u0020\u00A0\u000A]*([\u000A])+[\u0009\u0020\u00A0\u000A]*', '\n', news['content'], flags=re.UNICODE)
    print '----------------------'

    for c in content:
        print c,':',ord(c), 

    print '----------------------'
    print content
