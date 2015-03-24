#!/usr/bin/env python

import sys
import MySQLdb
import json
import codecs
import traceback

class StatLoader():
    def __init__(self, db_info, table_info=None):
        self.connectToDB(db_info)
        if table_info != None:
            self.statTable = table_info['statement_table']
        
    def connectToDB(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor


    # get one piece of news from given table
    def getStat(self):
        sql = 'SELECT id, content FROM %s' %(self.statTable)

        try:
            self.cursor.execute(sql)
            statDict = dict()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    statId = tmp[0]
                    statement = {"original": tmp[1]}
                    statDict[statId] = statement
            return statDict
        except Exception as e:
            print traceback.format_exc()
            return None

    def dumpStat(self, filename, statDict):
        # output as utf-8 file
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            json.dump(statDict, f, ensure_ascii=False, indent=2, sort_keys=True)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'statJson dbInfoJson outputJsonFile'
        exit(-1)

    statJsonFile = sys.argv[1]
    dbInfoJsonFile = sys.argv[2]
    outputJsonFile = sys.argv[3]

    with open(statJsonFile, 'r') as f:
        statConfig = json.load(f)

    with open(dbInfoJsonFile, 'r') as f:
        db_info = json.load(f)

    sl = StatLoader(db_info, statConfig)
    statDict = sl.getStat()
    sl.dumpStat(outputJsonFile, statDict)

