#!/usr/bin/env python3
import sys
from collections import defaultdict
import json

import numpy as np
import lda
from scipy.sparse import csr_matrix
from sklearn.grid_search import ParameterGrid

from RunExperiments import *
from misc import *
from Volc import *

# converting news to doc-word matrix (CSRMatrix)
def toDocWordMatrix(taggedLabelNewsList, volc=None, tfType='tf', allowedPOS=None, sentSep=",", wordSep=" ", tagSep='/'):
    numDoc = len(taggedLabelNewsList)
    # calculate word count in each document
    docTF = [defaultdict(int) for i in range(0, numDoc)]
    df = defaultdict(int)
    for i, taggedLabelNews in enumerate(taggedLabelNewsList):
        content = taggedLabelNews['news']['content_pos']
        wordIndexSet = set()
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if volc is not None and w not in volc:
                    continue
                if allowedPOS != None and t not in allowedPOS:
                    continue
                docTF[i][volc[w]] += 1
                wordIndexSet.add(volc[w])
        for wIndex in wordIndexSet:
            df[wIndex] += 1

    if tfType == 'tfidf':
        # get idf
        idf = getIDF(df, numDoc)
        # calc tfidf
        for tf in docTF:
            for wi in tf.keys():
                tf[wi] = tf[wi] * idf[wi]

    # convert to csr_matrix
    numV = len(volc)
    rows = list()
    cols = list()
    entries = list()
    for i, wCnt in enumerate(docTF):
        for wIndex, cnt in wCnt.items():
            rows.append(i)
            cols.append(wIndex)
            entries.append(cnt)
    W = csr_matrix((entries, (rows, cols)), shape=(numDoc, numV))
    return W

def getIDF(df, numDoc):
    idf = dict()
    for wi, f in df.items():
        idf[wi] = math.log(float(numDoc + 1) / (f + 1))
    return idf

def geti2W(volc):
    i2w = [volc.getWord(i) for i in range(0, len(volc))]
    return i2w

# vocab is a list (index -> word mapping)
def runLDA(W, vocab=None, nTopics=10, nIter=10, nTopicWords=10, randomState=1, outfile=sys.stdout):
    if nTopicWords == -1:
        nTopicWords = len(vocab) # all words
    model = lda.LDA(n_topics=nTopics, n_iter=nIter, random_state=randomState)
    model.fit(W)
    if vocab is not None:
        topicWord = model.topic_word_
        topicWordList = list()
        for i, topicDist in enumerate(topicWord):
            topicWords = list(np.array(vocab)[np.argsort(topicDist)][:-nTopicWords:-1])
            topicWordList.append(topicWords)
            print('Topic {}: {}'.format(i, ' '.join(topicWords)), file=outfile)
    return model

# print Topic-Word Matrix [topicNum x wordNum] (phi in literature)
def printTWMatrix(model, i2w, encoding='utf-8', outfile=sys.stdout):
    for w in i2w:
        outfile.write((w + ',').encode(encoding))
    np.savetxt(outfile, model.topic_word_, delimiter=',')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'TaggedLabelNewsJsonFile configFile', file=sys.stderr)
        exit(-1)

    taggedLabelNewsJsonFile = sys.argv[1]
    modelConfigFile = sys.argv[2]

    # load model config
    with open(modelConfigFile, 'r') as f:
        config = json.load(f)
    # read in tagged news json file
    with open(taggedLabelNewsJsonFile, 'r') as f:
        lnList = json.load(f)
    lnListInTopic = divideLabelNewsByTopic(lnList)
    topicSet = set([ln['statement_id'] for ln in lnList])
    newsIdList = { t:[ln['news_id'] for ln in lnListInTopic[t]] for t in topicSet }
    newsIdList['All'] = [ln['news_id'] for ln in lnList] 

    # load volcabulary file
    topicVolcDict = loadVolcFileFromConfig(config['volc'], topicSet)
    
    toRun = config['toRun']
    taskName = config['taskName']
    setting = config['setting']
    paramsIter = ParameterGrid(config['params'])

    if 'SelfTrainTest' in toRun:
        for t, lns in sorted(lnListInTopic.items(), key=lambda x:x[0]):
            # convert the news to doc-word count matrix
            volc = topicVolcDict[t]['main']
            i2w = geti2W(volc)
            for p in paramsIter:
                W = toDocWordMatrix(lns, volc=volc, tfType=p['feature'])
                model = runLDA(W, i2w, nTopics=p['nTopics'], nTopicWords = 100, nIter=p['nIters'], outfile=sys.stderr)
                X = model.doc_topic_
                y = np.array(getLabels(lns))
                expLog = RunExp.runTask(X, y, topicVolcDict, newsIdList[t], 'SelfTrainTest', p, topicId=t, **setting)
            with open('%s_SelfTrainTest_topic%d.pickle' % (taskName, t), 'w+b') as f:
                pickle.dump(expLog, f)

