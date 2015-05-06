#!/usr/bin/env python3
import sys
from collections import defaultdict
import json

import numpy as np
import lda
from scipy.sparse import csr_matrix


# converting news to doc-word matrix (CSRMatrix)
# w2i: word -> index (dict)
# i2w: index -> word (list)
def toDocWordMatrix(taggedNewsList, w2i=None, allowedPOS=None, 
        sentSep=",", wordSep=" ", tagSep='/'):
    if w2i == None:
        w2i = dict() # word -> index
        i2w = list() # index -> word
    numDoc = len(taggedNewsList)
    # calculate word count in each document
    docWords = [defaultdict(int) for i in range(0, numDoc)]
    for i, taggedNews in enumerate(taggedNewsList):
        content = taggedNews['content_pos']
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if allowedPOS != None and t not in allowedPOS:
                    continue
                if w not in w2i:
                    w2i[w] = len(w2i)
                    i2w.append(w)
                docWords[i][w2i[w]] += 1

    # convert to csr_matrix
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


def printModel(model, volc):
    pass

# print Topic-Word Matrix [topicNum x wordNum] (phi in literature)
def printTWMatrix(model, i2w, encoding='utf-8', outfile=sys.stdout):
    for w in i2w:
        outfile.write((w + ',').encode(encoding))
    np.savetxt(outfile, model.topic_word_, delimiter=',')

def saveVolc(filename, volc):
    if type(volc) == dict:
        with open(filename, 'w') as f:
            for w, i in sorted(volc.items(), key=lambda x:x[1]):
                print(w, file=f)
    elif type(volc) == list:
        with open(filename, 'w') as f:
            for w in volc:
                print(w, file=f)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage:', sys.argv[0], 'TaggedNewsJsonFile TopTopicWordFile TopicWordMatrixPrefix Volcabulary', file=sys.stderr)
        exit(-1)

    taggedNewsJsonFile = sys.argv[1]
    topTopicWordFile = sys.argv[2]
    topicWordMatrixFile = sys.argv[3]
    volcFile = sys.argv[4]

    # read in tagged news json file
    with open(taggedNewsJsonFile, 'r') as f:
        taggedNewsDict = json.load(f)

    taggedNewsList = list(taggedNewsDict.values())
    
    # parameters
    allowedPOS = set(['VA', 'NN', 'NR', 'AD', 'JJ', 'FW'])

    # convert the news to doc-word count matrix
    (W, w2i, i2w) = toDocWordMatrix(taggedNewsList, allowedPOS=allowedPOS)
    
    paramIter = [1]

    for p in paramIter:
        (model, topicWordList) = runLDA(W, i2w)
    
        #with open('TopicWordMatrix.txt', 'wb') as f:
        #    printTWMatrix(model, i2w, outfile=f)
    
        # save topic-word matrix
        np.save(topicWordMatrixFile, model.topic_word_)
        
    # save volcabulary file
    saveVolc(volcFile, i2w)

    with open(topicWordFile, 'w') as f:
        json.dump(topicWordList, f, ensure_ascii=False, indent=2)

