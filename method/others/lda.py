#!/usr/bin/env python3
import sys
from collections import defaultdict
import json

import numpy as np
import lda
from scipy.sparse import csr_matrix

# TODO:to remove stop words??
# converting news to doc-word matrix
def toDocWordMatrix(tagNewsList, w2i=None, denyPOS, 
        sentSep=",", wordSep=" ", tagSep='/'):
    if w2i == None:
        w2i = dict() # word -> index
        i2w = list() # index -> word
    numDoc = len(segNewsList)
    docWords = [defaultdict(int) for i in range(0, numDoc)]
    for i, segNews in enumerate(segNewsList):
        content = segNews['content_seg']
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if t not in denyPOS:
                    if w not in w2i:
                        w2i[w] = len(w2i)
                        i2w.append(w)
                    docWords[i][w2i[w]] += 1

    numV = len(w2i)
    rows = list()
    cols = list()
    entries = list()
    for i, wCnt in enumerate(docWords):
        for wIndex, cnt in wCnt.items():
            rows.append(i)
            cols.append(wIndex)
            entries.append(cnt)

    W = csr_matrix((entries, (rows, cols)), shape=(numDoc, numV))
    return (W, w2i, i2w)

# vocab is a list (index -> word mapping)
def runLDA(W, vocab, nTopics=10, nIter=10, nTopicWords = 100, randomState=1):
    model = lda.LDA(n_topics=nTopics, n_iter=nIter, random_state=randomState)
    model.fit(W)
    topicWord = model.topic_word_
    topicWordList = list()
    for i, topicDist in enumerate(topicWord):
        topicWords = list(np.array(vocab)[np.argsort(topicDist)][:-nTopicWords:-1])
        topicWordList.append(topicWords)
        print('Topic {}: {}'.format(i, ' '.join(topicWords)))
    
    return (model, topicWordList)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'tagNewsJsonFile topicWordFile', file=sys.stderr)
        exit(-1)

    tagNewsJsonFile = sys.argv[1]
    topicWordFile = sys.argv[2]

    with open(tagNewsJsonFile, 'r') as f:
        tagNewsDict = json.load(f)

    tagNewsList = list(tagNewsDict.values())

    (W, w2i, i2w) = toDocWordMatrix(tagNewsList, denyPOS=set())
    (model, topicWordList) = runLDA(W, i2w)

    with open(topicWordFile, 'w') as f:
        json.dump(topicWordList, f, ensure_ascii=False, indent=2)

