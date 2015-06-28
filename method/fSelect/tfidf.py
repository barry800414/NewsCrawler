
import sys
from collections import defaultdict
import math
from misc import *
from Volc import Volc

def calcTFIDF(lnList, tfType, allowedPOS):
    tf = defaultdict(int)
    df = defaultdict(int)
    # calculate tf & df
    for ln in lnList:
        content = ln['news']['content_pos']
        wordSet = set()
        for sent in content.split(','):
            for wt in sent.split(' '):
                (w, t) = wt.split('/')
                if allowedPOS is not None and t not in allowedPOS:
                    continue
                tf[w] += 1
                wordSet.add(w)
        for w in wordSet:
            df[w] += 1

    if tfType == 'tf':
        return tf
    elif tfType == 'df':
        return df
    elif tfType == 'tfidf':
        docNum = len(lnList)
        tfidf = dict()
        for w, tfCnt in tf.items():
            dfCnt = df[w]
            tfidf[w] = tfCnt * math.log(float(docNum + 1) / (dfCnt + 1))
        return tfidf

def printWordValue(wvDict, sort=True, reverse=True, outfile=sys.stdout):
    wvList = list(wvDict.items())
    if sort:
        wvList.sort(key=lambda x:x[1], reverse=reverse)
    for word, value in wvList:
        print(word, value, sep=':', file=outfile)

def saveAsVolc(wvList, p, filename):
    volc = Volc()
    nWords = round(len(wvList) * p)
    for i in range(0, nWords):
        w = wvList[i][0]
        volc.addWord(w)
    volc.save(filename)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'taggedLabelNewsJsonFile type(tf, tfidf) outFilePrefix', file=sys.stderr) 
        exit(-1)

    inJsonFile = sys.argv[1]
    tfType = sys.argv[2]
    outFilePrefix = sys.argv[3]

    with open(inJsonFile, 'r') as f:
        taggedLN = json.load(f)
    taggedLNInTopic = divideLabelNewsByTopic(taggedLN)
    
    allowedPOS = set(["VA", "VV", "NN", "NR", "AD", "JJ"])
    allowedPOS = set(["NN", "NR"])
    tfidfDict = calcTFIDF(taggedLN, tfType, allowedPOS)
    with open(outFilePrefix + '_TAll.txt', 'w') as f:
        printWordValue(tfidfDict, outfile=f)

    for topicId, lnList in sorted(taggedLNInTopic.items(), key=lambda x:x[0]):
        tfidfDict = calcTFIDF(lnList, tfType, allowedPOS)
        wvList = sorted(tfidfDict.items(), key=lambda x:x[1], reverse=True)
        #for i in range(1, 11):
        #    p = i * 0.1
        #    saveAsVolc(wvList, p, outFilePrefix + '_T%d_P%d.volc' % (topicId, int(p*100)))
        with open(outFilePrefix + '_T%d.txt' % (topicId), 'w') as f:
            printWordValue(tfidfDict, outfile=f)


