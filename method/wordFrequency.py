#!/usr/bin/env python3 

import sys
import json
from collections import defaultdict

'''
This code is for calculating word frequency in corpus
Date: 2015/03/05
Author: Wei-Ming Chen
'''

SENT_SEP=','
WORD_SEP=' '
POS_SEP='/'

# divide the corpus into several topic
# return a dict ('statement_id' -> 'corpus')
def divideTopic(taggedLabelNewsList):
    topicCorpus = dict()
    for tln in taggedLabelNewsList:
        if tln['statement_id'] not in topicCorpus:
            topicCorpus[tln['statement_id']] = list()
        topicCorpus[tln['statement_id']].append(tln)
    return topicCorpus

# calculate frequency in of word-tag whole corpus
# return a dict of dicts, tf[t][w] means the frequency of word with tag t
# TODO: title & content?
def calcWordTagTFInCorpus(taggedLabelNewsList, sentSep=SENT_SEP, 
        wordSep=WORD_SEP, posSep=POS_SEP):
    tf = defaultdict(dict)
    for tln in taggedLabelNewsList:
        calcWordTagTF(tln['news']['content_tagged'],tf=tf, sentSep=sentSep,
                wordSep=wordSep, posSep=posSep)
    return tf

# calculating frequency of word-tag in text
# tf: a dict of dicts, tf[t][w] means the frequency of word with tag t
def calcWordTagTF(text, tf=None, sentSep=SENT_SEP, wordSep=WORD_SEP, 
        posSep=POS_SEP):
    if tf == None:
        tf = defaultdict(dict)

    sentList = text.split(sentSep)
    for sent in sentList:
        taggedWordList = sent.split(wordSep)
        for tw in taggedWordList:
            buf = tw.split(posSep)
            w = buf[0] #word
            t = buf[1] #POS tagger
            if w not in tf[t]:
                tf[t][w] = 1
            else:
                tf[t][w] += 1
    return tf

# word total order
# word&tag total order
# order in each kind of tag
def getWFLists(tf, statId, folder='./tf'):
    
    # word total order &  word&tag total order
    sumTf = defaultdict(int)
    wtList = list()
    for t, wCnt in tf.items():
        for w, cnt in wCnt.items():
            sumTf[w] += cnt
            wtList.append(('%s/%s' % (w,t), cnt))
    
    wList = list(sumTf.items())
    wList.sort(key = lambda x:x[1], reverse=True)
    wtList.sort(key = lambda x:x[1], reverse=True)

    # order in each kind of tag
    wInOnePOSList = dict()
    for t, wCnt in tf.items():
        tmp = list(wCnt.items())
        tmp.sort(key = lambda x:x[1], reverse=True)
        wInOnePOSList[t] = tmp

    return (wList, wtList, wInOnePOSList)


def writeWFList(wfList, filename):
    with open(filename, 'w') as fout:
        for w, f in wfList:
            print(w, f, sep='\t', file=f)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'taggedNewsJson', file=sys.stderr)
        exit(-1)
    
    taggedNewsJson = sys.argv[1]

    with open(taggedNewsJson, 'r') as f:
        taggedLabelNewsList = json.load(f)

    topicCorpus = divideTopic(taggedLabelNewsList)
    
    wordList = { "NN": dict(), "NR": dict(), "VV": dict(), 
            "AD": dict(), "VA": dict() }
    for statId, topicNews in topicCorpus.items():
        tf = calcWordTagTFInCorpus(topicNews)
        (wList, wtList, wInOnePOSList) = getWFLists(tf, statId)
        '''
        writeWFList(wList, 'Stat%s_WordFrequency.txt')
        writeWFList(wtList, 'Stat%s_WordTagFrequency.txt')
        for pos, tmpList in wInOnePOSList.items(): 
            writeWFList(tmpList, 'Stat%s_%s_WordFrequency.txt')
        '''
        for pos in wordList.keys():
            wordList[pos][statId] = { w:f for w, f in wInOnePOSList[pos] }
    
    for pos in wordList.keys():
        with open('%s_List.json' %(pos),'w') as f:
            json.dump(wordList[pos], f, ensure_ascii=False)

