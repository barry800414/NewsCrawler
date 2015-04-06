
import sys
import json
import MySQLdb
import traceback

import NewsLoader 
import filter

'''
Add more topic news into database 
LastUpdate: 2015/03/31
'''

MAX_F1 = -1.0
MAX_KEYWORDS = None
MAX_REMAIN = None
MAX_MINF = 0

def recursiveTry(nl, topicId, topicNewsList):
    irrel = set()
    nl.cursor.execute("SELECT DISTINCT(news_id) FROM `statement_news` \
            WHERE relevance='irrelevant' and statement_id = %d" % topicId)
    while True:
        tmp = nl.cursor.fetchone()
        if tmp == None: break
        irrel.add(tmp[0])
    
    rel = set()
    nl.cursor.execute("SELECT DISTINCT(news_id) FROM `statement_news` \
            WHERE relevance='relevant' and statement_id = %d" % topicId)
    while True:
        tmp = nl.cursor.fetchone()
        if tmp == None: break
        rel.add(tmp[0])
    
    print rel
    print irrel

    # find already labeled data
    labeledTNL = list()
    for tn in topicNewsList:
        newsId = tn['news']['id']
        if newsId in rel and newsId in irrel:
            labeledTNL.append(tn)

    print '#labeled topic %d news:' % (topicId), len(labeledTNL)
    for m in range(1, 6):
        __recursiveFunc(labeledTNL, keywords, m, irrel, 
                rel, 0, len(keywords), [False for i in range(0, len(keywords))])
    #global MAX_F1, MAX_KEYWORDS, MAX_REMAIN
    #print MAX_F1, MAX_KEYWORDS, MAX_REMAIN

def __recursiveFunc(topicNewsList, keywords, minFreq, irrel, rel, nowLayer, maxLayer, selected):
    if nowLayer == maxLayer:
        selected = [keywords[i] for i, b in enumerate(selected) if b]
        noKeyword = set()
        hasKeyword = set()
        if len(selected) == 0:
            return 
        for tn in topicNewsList:
            news = tn['news']
            if not f.contain_keywords(news, selected, minFreq):
                noKeyword.add(news['id'])
            else:
                hasKeyword.add(news['id'])
        eval(rel, irrel, hasKeyword, noKeyword, selected, minFreq)

    else:
        for b in [False, True]:
            selected[nowLayer] = b
            __recursiveFunc(topicNewsList, keywords, minFreq, irrel, rel, 
                    nowLayer+1, maxLayer, selected)

def eval(rel, irrel, hasKeyword, noKeyword, selected=None, minFreq=None):   
    TP = len(rel&hasKeyword)
    FP = len(irrel&hasKeyword)
    FN = len(rel&noKeyword)
    TN = len(irrel&noKeyword)
    if TP+FP != 0:
        P = float(TP)/(TP+FP)
    else:
        P = 0.0
    if TP+FN != 0:
        R = float(TP)/(TP+FN)
    else:
        R = 0.0
    if TP+FP+FN+TN != 0:
        ACCU = float(TP+TN)/(TP+FP+FN+TN)
    else:
        ACCU = 0.0
    if P+R != 0.0:
        F1 = (2.0*P*R) / (P+R)
    else:
        F1 = 0.0
    global MAX_F1, MAX_KEYWORDS, MAX_REMAIN, MAX_MINF
    if F1 >= MAX_F1:
        MAX_F1 = F1
        if selected != None:
            MAX_KEYWORDS = list(selected)
        if minFreq != None:
            MAX_MINF = minFreq
        MAX_REMAIN = len(noKeyword)
    print 'Keywords: ',
    if selected != None:
        for w in selected:
            print w.encode('utf-8'), 
    print '\n\tHas\tNo\t'
    print 'rel\t%d\t%d\t%d' % (TP, FN, TP+FN)
    print 'irrel\t%d\t%d\t%d' % (FP, TN, FP+TN)
    print '\t%d\t%d' % (TP+FP, FN+TN)
    print 'Precision:%f\tRecall:%f\nACCU:%f\tF1:%f' %(P, R, ACCU, F1)
    print 'MinFreq:', minFreq

def getOriginalTopicNews(nl, topicId):
    sql = 'SELECT DISTINCT(news_id) FROM topic_news_backup WHERE topic_id = %d' % topicId 
    try:
        newsIdSet = set()
        nl.cursor.execute(sql)
        while True:
            tmp = nl.cursor.fetchone()
            if tmp == None: break
            newsIdSet.add(tmp[0])
        return newsIdSet
    except Exception as e:
        print traceback.format_exc()
        return None

class TopicNewsInserter():
    def __init__(self, db_info, table_info=None):
        self.connectToDB(db_info)
        if table_info != None:
            self.topicNewsTable = table_info['topic_news_table']
            #self.topicTable = table_info['topic_table']
        
    def connectToDB(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def deleteTopicNews(self, topicNewsIdSet):
        for topicNewsId in topicNewsIdSet:
            sql = 'DELETE FROM %s WHERE id=%d' % (self.topicNewsTable, topicNewsId)
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except Exception as e:
                print traceback.format_exc()
                self.db.rollback()
    
    def insertTopicNews(self, topicIdNewsIdSet):
        for topicId, newsId in topicIdNewsIdSet:
            sql = 'INSERT INTO %s (topic_id, news_id) VALUES (%d, "%s")' % (
                    self.topicNewsTable, topicId, newsId)
            print(sql)
            try:
                self.cursor.execute(sql)
                self.db.commit()
            except Exception as e:
                print traceback.format_exc()
                self.db.rollback()

                


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, "Usage:", sys.argv[0], "topicId topicConfigJson dbConfigJson"
        exit(-1)

    topicId = int(sys.argv[1])
    topicConfigJson = sys.argv[2]
    dbConfigJson = sys.argv[3]

    with open(topicConfigJson, 'r') as f:
        topicConfig = json.load(f)
    with open(dbConfigJson, 'r') as f:
        dbConfig = json.load(f)

    nl = NewsLoader.NewsLoader(dbConfig, {"topic_news_table": "topic_news_all_backup"})
    f = filter.NewsFilter(dbConfig)

    topicNewsDict = nl.getTopicNews(topicIdList=[topicId], 
            limitNum=-1, corpusTable='merge_necessary')
    
    # topicNewsDict[topicId] is a list of topicNews
    # topicNews['topicNewsId'] is the id of topicNews
    # topicNews['news'] is the news
    topicNewsList = topicNewsDict[topicId]
    
    configs = topicConfig['topic_configs']
    keywords = configs[topicId-1]['keywords']

    #minFreq = configs[topicId-1]['minimum_frequency'] #unsafe
    minFreq = 4
    maxLen = 1000

    oriTopicNews = getOriginalTopicNews(nl, topicId)
    print '#original topic news:', len(oriTopicNews)
    toInsert = set()
    cnt = cnt2 = cnt3 = 0
    for tn in topicNewsList:
        news = tn['news']
        newsId = news['id']
        if f.contain_keywords(news, keywords, minFreq) and len(news['content']) <= maxLen and newsId not in oriTopicNews:
            toInsert.add((topicId, news['id']))
        if f.contain_keywords(news, keywords, minFreq):
            cnt += 1
        if len(news['content']) <= maxLen:
            cnt2 += 1
        if newsId not in oriTopicNews:
            cnt3 += 1
    print '#news containing %d keywords:' % minFreq, cnt
    print '#news length < %d:' % maxLen, cnt2
    print '#news not in original topic news: ', cnt3

    print '#news to be inserted:', len(toInsert)  

    #tni = TopicNewsInserter(dbConfig, {"topic_news_table": "topic_news"})
    #tni.insertTopicNews(toInsert)
    
    #for recursively (brute force) find all possible combination
    #recursiveTry(nl, topicId, topicNewsList)
    #print MAX_F1, MAX_KEYWORDS, MAX_REMAIN, MAX_MINF
    
