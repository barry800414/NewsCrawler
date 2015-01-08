#!/usr/bin/env python

import sys
import MySQLdb
import json
import codecs
from NewsLoader import NewsLoader


class LabelLoader():
    defaultLabelColumn = ["valid_format", "relevance", 
        "mention_agree", "mention_disagree", "label", "labeler"]
    
    def __init__(self, db_info, table_info):
        self.connectToDB(db_info)
        self.label_table = table_info['label_table']
        self.statement_table = table_info['statement_table']
        self.topic_table = table_info['topic_table']

    def connectToDB(self, db_info):
        # initialize the connection to database
        db = MySQLdb.connect(db_info['host'], db_info['user'],
            db_info['password'], db_info['database'], 
            port=db_info['port'], charset='utf8', 
            init_command='SET NAMES UTF8')
        cursor = db.cursor()
        self.db = db
        self.cursor = cursor

    def __convert_to_sql(self, column, prefix=None):
        s = ''
        if prefix != None:
            for c in column[0:-1]:
                s = s + '%s.%s, ' % (prefix, c)
            s = s + '%s.%s' % (prefix, column[-1])
        else:
            for c in column[0:-1]:
                s = s + '%s, ' % (c)
            s = s + '%s' % (column[-1])
        return s

    def __gen_where(self, where_config, prefix=None):
        valid_format = whereConfig['valid_format']
        relevance = whereConfig['relevance']
        label = whereConfig['label']

        if prefix == None:
            prefix = ''
        else:
            prefix = prefix + '.'
        s = ''
        for columnName, acceptValues in whereConfig.items():
            if len(acceptValues)!= 0:
                if len(s) != 0:
                    s = s + ' AND '
                s = s + '('
                for c in acceptValues[0:-1]:
                    s = s + "%s%s='%s' OR " % (prefix, columnName, c)
                s = s + "%s%s='%s')" % (prefix, columnName, acceptValues[-1])

        return s

        

    # get labels by certain topic
    # labelColumns = ["valid_form", "relevance", "mention_agree", 
    # "mention_disagree", "label", "labeler"]
    def getLabelByTopic(self, whereConfig, topicId, labelColumns = defaultLabelColumn):
               
        sql = '''SELECT C.statement_id, B.content, C.news_id, %s 
                 FROM %s as A, %s as B, %s as C
                 WHERE B.topic_id = A.id AND B.id = C.statement_id AND %s
              ''' % (self.__convert_to_sql(labelColumns, 'C'), self.topic_table, 
                      self.statement_table, self.label_table, 
                      self.__gen_where(whereConfig, 'C'))
        print sql
        try:
            self.cursor.execute(sql + ' AND B.topic_id = %s', (topicId, ))
            labelList = list()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    label = dict()
                    label['statement_id'] = tmp[0]
                    label['statement'] = tmp[1]
                    label['news_id'] = tmp[2]
                    for i, c in enumerate(labelColumns):
                        label[c] = tmp[3+i]
                    labelList.append(label)
            return labelList
        except Exception, e:
            print e
            return None


    def getLabelById(self, whereConfig, statementId = None, newsId = None,  
            labelColumns = defaultLabelColumn):
        sql = '''SELECT B.statement_id, A.content, B.news_id, %s
                 FROM %s as A, %s as B
                 WHERE A.id = B.statement_id AND %s
              ''' % (self.__convert_to_sql(labelColumns, 'B'), 
                      self.statement, self.label_table, 
                      self.__gen_where(whereConfig, 'C'))

        print sql
        try:
            if statementId != None:
                if newsId != None:
                    self.cursor.execute(sql + ' AND B.statement_id = %s AND B.news_id = %s', (statementId, newsId))
                else:
                    self.cursor.execute(sql + ' AND B.statement_id = %s', (statementId, ))
            else:
                if newsId != None:
                    self.cursor.execute(sql + ' AND B.news_id = %s', (newsId, ))
                else:
                    self.cursor.execute(sql)

            labelList = list()
            while True:
                tmp = self.cursor.fetchone()
                if tmp == None:
                    break
                else:
                    label = dict()
                    label['statement_id'] = tmp[0]
                    label['statement'] = tmp[1]
                    label['news_id'] = tmp[2]
                    for i, c in enumerate(labelColumns):
                        label[c] = tmp[3+i]
                    labelList.append(label)
            return labelList
        except Exception, e:
            print e
            return None

    def getLabelNewsById(self, newsLoader, swhereConfig, tatementId, newsId,  
            corpusTable, labelColumns = defaultLabelColumn):

        labelList = self.getLabelById(whereConfig, statementId, newsId, labelColumns)
        for label in labelList:
            label['news'] = newsLoader.getNews(label['news_id'], corpusTable)
        return labelList 

    def getLabelNewsByTopic(self, newsLoader, whereConfig, topicId, corpusTable, 
        labelColumns = defaultLabelColumn):
        labelList = self.getLabelByTopic(whereConfig, topicId, labelColumns)
        for label in labelList:
            label['news'] = newsLoader.getNews(label['news_id'], corpusTable)
        return labelList

    def dumpLabels(self, filename, labelList):
        # output as utf-8 file
        with codecs.open(filename, 'w', encoding='utf-8') as f:
            json.dump(labelList, f, ensure_ascii=False, indent=2, sort_keys=True)


'''
label_loader_json = {
    "label_table": "statement_news",
    "statement_table": "statement", 
    "topic_table": "topic",
    "corpus_table": "merge",
    "topic_id": 1,
    "statement_id": "1",
    "news_id": "ltn0000001",
    "query_type": "topic/id",
    "get_news": True/False
}
'''

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'label_loader_json db_info_json output_json_file'
        exit(-1)

    label_loader_json_file = sys.argv[1]
    db_info_json_file = sys.argv[2]
    output_json_file = sys.argv[3]

    with open(label_loader_json_file, 'r') as f:
        config = json.load(f)
    with open(db_info_json_file, 'r') as f:
        db_info = json.load(f)

    loader = LabelLoader(db_info, config) 
    query_type = config['query_type']
    get_news = config['get_news']
    whereConfig = config['where_config']
    if query_type == 'topic':
        topicId = config['topic_id']
        if get_news:
            newsLoader = NewsLoader(db_info)
            corpusTable = config['corpus_table']
            labelList = loader.getLabelNewsByTopic(newsLoader, whereConfig,
                    topicId, corpusTable)
        else:
            labelList = loader.getLabelByTopic(whereConfig, topicId)
    elif query_type == 'id':
        statementId = None
        newsId = None
        if 'statement_id' in config:
            statementId = config['statement_id']
        if 'news_id' in config:
            newsId = config['news_id']
        if get_news:
            newsLoader = NewsLoader.NewsLoader(db_info)
            corpusTable = config['corpus_table']
            labelList = loader.getLabelNewsById(newsLoader, whereConfig, 
                    statementId, newsId, corpusTable)
        else:
            labelList = loader.getLabelById(whereConfig, statementId, newsId)

    loader.dumpLabels(output_json_file, labelList)
