#!/usr/bin/env python

import sys
import MySQLdb
import json

from LabelNewsLoader import LabelNewsLoader
from NewsLoader import NewsLoader

'''
The newer version for cleaning news
1. selecting news only when it is necessary to be preprocessed (labeled as valid),
   store them as a file, and update the "to_clean" field in corpus table
2. cleaning news by Ran-Yu as a new file
3. updating cleaned news to database, update the "cleaned" field in corpus table
Last Update: 2015/03/31
'''

def initDBConnection(dbInfo):
    db = MySQLdb.connect(dbInfo['host'], dbInfo['user'],
        dbInfo['password'], dbInfo['database'], 
        port=dbInfo['port'], charset='utf8', 
        init_command='SET NAMES UTF8')
    return db

def updateToCleanField(db, corpusTable, newsIdSet):
    # initialize the connection to database
    cursor = db.cursor()
    for newsId in newsIdSet:
        sql = 'UPDATE `%s` SET to_clean=1 WHERE id="%s"' % (corpusTable, newsId)
        print sql
        try:
            cursor.execute(sql)
            db.commit()
        except Exception as e:
            print e
            db.rollback()
        
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'dbInfoJsonFile outputNewsFile'
        exit(-1)
    dbInfoJsonFile = sys.argv[1]
    outputNewsFile = sys.argv[2]
    
    with open(dbInfoJsonFile, 'r') as f:
        dbInfo = json.load(f)
    
    config = {
        "label_table": "statement_news",
        "statement_table": "statement", 
        "topic_table": "topic",
        "corpus_table": "merge_necessary_clean",
        "topic_id": [2, 3, 4, 5, 6, 13, 16],
        "where_config": {
            "relevance": [],
            "valid_format": ["valid", "small_error"],
            "label": []
        },
        "query_type": "topic",
        "get_news": False,
        "merge": False
    }

    lnLoader = LabelNewsLoader(dbInfo, config)
    nLoader = NewsLoader(dbInfo)

    labelNewsList = lnLoader.getLabelNewsList(config)
    
    # find all news id to be cleaned
    newsIdSet = set()
    for labelNews in labelNewsList:
        newsIdSet.add(labelNews['news_id'])
    print "#news to be cleaned:", len(newsIdSet)

    # update the "to_clean" field in corpus table 
    #updateToCleanField(initDBConnection(dbInfo), config['corpus_table'], newsIdSet)

    
    newsDict = dict()
    for newsId in newsIdSet:
        newsDict[newsId] = nLoader.getNews(newsId, config['corpus_table'])

    nLoader.dumpNews(outputNewsFile, newsDict)
    
