#!/usr/bin/env python

import sys
import MySQLdb
import json



def initDBConnection(dbInfo):
    db = MySQLdb.connect(dbInfo['host'], dbInfo['user'],
        dbInfo['password'], dbInfo['database'], 
        port=dbInfo['port'], charset='utf8', 
        init_command='SET NAMES UTF8')
    return db

def updateNews(db, corpusTable, newsDict, manualClean=0):
    # initialize the connection to database
    cursor = db.cursor()
    for newsId, news in newsDict.items():
        news = stripNews(news)
        print newsId
        try:
            sql = 'UPDATE `%s`' % (corpusTable)
            cursor.execute(sql + u" SET title=%s, content=%s, cleaned=1, manually_clean=%s WHERE id=%s", (
                news['title'], news['content'], manualClean, newsId))
            db.commit()
        except Exception as e:
            print e
            print news['title'].encode('utf-8')
            print news['content'].encode('utf-8')
            db.rollback()
            break

def stripNews(news):
    news['title'] = news['title'].strip()
    news['content'] = news['content'].strip()
    return news
        
if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'dbInfoJson cleanedNewsJson manualClean(0/1)'
        exit(-1)
    dbInfoJsonFile = sys.argv[1]
    cleanedNewsJsonFile = sys.argv[2]
    manualClean = int(sys.argv[3])
    
    with open(dbInfoJsonFile, 'r') as f:
        dbInfo = json.load(f)
    
    with open(cleanedNewsJsonFile, 'r') as f:
        newsDict = json.load(f)

    corpusTable = 'merge_necessary_clean'
    db = initDBConnection(dbInfo)

    updateNews(db, corpusTable, newsDict, manualClean)

    
