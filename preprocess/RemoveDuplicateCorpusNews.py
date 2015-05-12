#!/usr/bin/env python

import sys
import MySQLdb
import json
import math


# remove duplicated news under certain topic
def convertToNewsList(newsDict):
    newsList = list()
    for newsId, news in newsDict.items():
        news['id'] = newsId
        newsList.append(news)
    newsList.sort(key=lambda x:x['id'])
    return newsList

# all pairs compare
def getDupNewsIds(newsList):    
    # calculating term frequency
    for news in newsList:
        news['title_tf'] = getTF(news['title'])
        news['content_tf'] = getTF(news['content'])

    # finding duplicated news
    toRemove = set()
    total_task = (len(newsList) * (len(newsList) - 1)) / 2
    cnt = 0
    for i, n1 in enumerate(newsList):
        for j in range(i+1, len(newsList)):
            n2 = newsList[j]
            if n2['id'] in toRemove:
                continue
            if isSameNews(n1, n2):
                toRemove.add(n2['id'])
            cnt = cnt + 1
            if cnt % 1000 == 0:
                print >>sys.stderr, 'Progress(%d/%d)' % (cnt, total_task)
    
    return toRemove

def getTF(string):
    tf = dict()
    for c in string:
        if c not in tf:
            tf[c] = 1
        else:
            tf[c] += 1
    return tf

def isSameNews(news1, news2):
    title_sim = cosSim(news1['title_tf'], news2['title_tf'])
    content_sim = cosSim(news1['content_tf'], news2['content_tf'])
    if title_sim > 0.5 and content_sim > 0.9:
        
        print '---------------------------------------'
        print 'Title Sim:' + str(title_sim)
        print 'Content Sim:' + str(content_sim)
        print 'NewsID1:' + news1['id']
        print 'NewsID2:' + news2['id']
        print 'Title1:' + news1['title'].encode('utf-8')
        print 'Title2:' + news2['title'].encode('utf-8')
        print 'Url1:' + news1['url']
        print 'Url2:' + news2['url']
        sys.stdout.flush()
        '''
        print 'Content1:' + news1['content'].encode('utf-8')
        print 'Content2:' + news2['content'].encode('utf-8')
        for key,value in news1['content_tf'].items():
            print key.encode('utf-8') + ':' + str(value)
        for key,value in news2['content_tf'].items():
            print key.encode('utf-8') + ':' + str(value)
        '''
        return True
    else:
        return False

def cosSim(tf1, tf2):
    value = 0.0
    common_term = set(tf1.keys()) & set(tf2.keys())
    for t in common_term:
        value += tf1[t] * tf2[t] 
    norm = 0.0
    for v in tf1.values():
        norm += v * v
    value = value / math.sqrt(norm)
    norm = 0.0
    for v in tf2.values():
        norm += v * v
    value = value / math.sqrt(norm)
    return value

def remove_data_from_table(table_name, topic_id, news_id_set):
    for news_id in news_id_set:
        try:
            sql = 'DELETE FROM `%s` WHERE ' % table_name
            cursor.execute(sql + " topic_id=%s AND news_id=%s", (topic_id, news_id))
            db.commit()
        except Exception, e:
            print '%s' % e
            db.rollback()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'newsJson dbInfoJson'
        exit(-1)

    newsJsonFile = sys.argv[1]
    dbInfoJsonFile = sys.argv[2]

    with open(newsJsonFile, 'r') as f:
        newsDict = json.load(f)

    newsList = convertToNewsList(newsDict)
    toRemove = getDupNewsIds(newsList)
    print('#To remove: ', toRemove)


