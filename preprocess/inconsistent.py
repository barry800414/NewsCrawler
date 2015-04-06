#!/usr/bin/env python

import sys
import MySQLdb
import json
from  time import *

# filter the news with important keywords
class DataInconsistent():
    def __init__(self, db_info):
        self.connect_to_db(db_info)

    def connect_to_db(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def getStatementNews(self):
        sql = 'SELECT * FROM statement_news'
        try: 
            self.cursor.execute(sql)
            lnList = list()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                ln = dict()
                ln['id'] = tmp[0]
                ln['statement_id'] = tmp[1]
                ln['news_id'] = tmp[2]
                ln['valid_format'] = tmp[3]
                ln['relevance'] = tmp[4]
                ln['mention_agree'] = tmp[5]
                ln['mention_disagree'] = tmp[6]
                ln['label'] = tmp[7]
                ln['labeler'] = tmp[8]
                ln['generated_time'] = tmp[9]
                lnList.append(ln)  
            return lnList
        except Exception, e:
            print e


    def toStatNewsDict(self, lnList):
        snDict = dict()
        for ln in lnList:
            s = ln['statement_id']
            n = ln['news_id']
            if (s, n) not in snDict:
                snDict[(s, n)] = list()
            snDict[(s, n)].append(ln)
        return snDict

    # detect duplicated statement-news (in short time)
    def detectDuplicate(self, snDict):
        for sn, lns in snDict.items():
            for i in range(0, len(lns)):
                ln1 = lns[i]
                for j in range(i+1, len(lns)):
                    ln2 = lns[j]
                    delta = ln1['generated_time'] - ln2['generated_time']
                    if abs(delta.total_seconds()) < 20:
                        print 'Duplicated:', ln1['statement_id'], ln1['news_id']
                        cmd = 'SELECT * FROM statement_news WHERE statement_id = %s and news_id = "%s"' % (ln1['statement_id'], ln2['news_id'])
                        print cmd

    def detectValidFormat(self, snDict):
        cnt = 0
        for sn, lns in snDict.items():
            for i in range(0, len(lns)):
                ln1 = lns[i]
                ln1v = ln1['valid_format']
                for j in range(0, len(lns)):
                    if i == j:
                        continue
                    ln2 = lns[j]
                    ln2v = ln2['valid_format']
                    if (ln1v == 'valid' or ln1v == 'small_error') and (ln2v == 'invalid'):
                        print 'Valid Format Inconsistent(1: valid or small_error, 2:invalid): ', ln1['statement_id'], ln1['news_id'], len(lns)
                        cnt += 1
        print "#valid format inconsistent:", cnt
                        

    def detectRelevance(self, snDict):
        cnt = 0
        for sn, lns in snDict.items():
            for i in range(0, len(lns)):
                ln1 = lns[i]
                ln1r = ln1['relevance']
                for j in range(0, len(lns)):
                    if i == j:
                        continue
                    ln2 = lns[j]
                    ln2r = ln2['relevance']
                    if ln1r == 'relevant' and (ln2r == 'irrelevant' or ln2r == ''):
                        print 'Relevance Inconsistent(1: relevant, 2:irrelevant): ', ln1['statement_id'], ln1['news_id'], len(lns)
                        cnt += 1
        print "#Relevance inconsistent:", cnt
                        



    def run(self):
        lnList = self.getStatementNews()
        snDict = self.toStatNewsDict(lnList)
        self.detectDuplicate(snDict)
        self.detectValidFormat(snDict)
        self.detectRelevance(snDict)


'''
topic_json = {
    "src_table": "merge",
    "target_table": "topic_news_all",
    "topic_configs": [ topic_config1, topic_config2 ...]
}

topic_config = {
    "id": ...,
    "target_table": ...,
    "src_table": ...,
    "keywords": [...],
    "minimum_frequency": .. 
}
'''


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'db_info_json'
        exit(-1)

    db_info_json_file = sys.argv[1]

    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    di = DataInconsistent(db_info)
    di.run()
