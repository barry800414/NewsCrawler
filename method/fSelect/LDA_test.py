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
def toDocWordMatrix(taggedLabelNewsList, volc=None, tfType='tf', allowedPOS=None,
        minCnt=5, sentSep=",", wordSep=" ", tagSep='/'):
    if volc is None:
        volc = Volc()
    numDoc = len(taggedLabelNewsList)
    # calculate word count in each document
    docTF = [defaultdict(int) for i in range(0, numDoc)]
    df = defaultdict(int)
    for i, taggedLabelNews in enumerate(taggedLabelNewsList):
        content = taggedLabelNews['news']['content_pos']
        wordSet = set()
        for sent in content.split(sentSep):
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if w not in volc and volc.lockVolc:
                    continue
                if allowedPOS != None and t not in allowedPOS:
                    continue
                if w not in volc:
                    volc.addWord(w)
                docTF[i][w] += 1
                wordSet.add(w)
        for w in wordSet:
            df[w] += 1
        if (i+1) % 100 == 0:
            print('%cProgress:(%d/%d)' % (13, i+1, len(taggedLabelNewsList)), end='', file=sys.stderr)
    print('', file=sys.stderr)

    if tfType == 'tfidf':
        # get idf
        idf = getIDF(df, numDoc)
        # calc tfidf
        for tf in docTF:
            for w in tf.keys():
                tf[w] = tf[w] * idf[w]

    if minCnt > 0:
        print('Removing words by document frequency < %d' % minCnt, file=sys.stderr)
        print('Original Volc size:', len(volc), file=sys.stderr)
        DF = convertToWordIndexDF(df, volc)
        DF = volc.shrinkVolcByDocF(DF, minCnt)
        print('After removeing:', len(volc), file=sys.stderr)

    # convert to csr_matrix
    numV = len(volc)
    rows = list()
    cols = list()
    entries = list()
    wordIndexSet = set()
    for i, wCnt in enumerate(docTF):
        for w, cnt in wCnt.items():
            if w not in volc:
                continue
            wordIndexSet.add(volc[w])
            rows.append(i)
            cols.append(volc[w])
            entries.append(cnt)
    print(len(wordIndexSet), file=sys.stderr)
    W = csr_matrix((entries, (rows, cols)), shape=(numDoc, numV))
    print('X.shape:', W.shape, file=sys.stderr)
    return W

def convertToWordIndexDF(df, volc):
    DF = defaultdict(int)
    for w, cnt in df.items():
        DF[volc[w]] += cnt
    return DF

def getIDF(df, numDoc):
    idf = dict()
    for w, f in df.items():
        idf[w] = math.log(float(numDoc + 1) / (f + 1))
    return idf

def geti2W(volc):
    if volc is None:
        return None
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

def getLabelIndex(lns):
    labelIndex = list()
    noLabelIndex = list()
    for i,ln in enumerate(lns):
        if ln['label'] == '':
            noLabelIndex.append(i)
        else:
            labelIndex.append(i)
    return (labelIndex, noLabelIndex)

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
            volc = topicVolcDict[t]['main'] if topicVolcDict[t] is not None and 'main' in topicVolcDict[t] else None
            i2w = geti2W(volc)
            for p in paramsIter:
                print('Converting to doc-word matrix ...', file=sys.stderr)
                W = toDocWordMatrix(lns, volc=volc, tfType=p['feature'])
                model = runLDA(W, i2w, nTopics=p['nTopics'], nTopicWords = 100, nIter=p['nIters'], outfile=sys.stderr)
                allX = model.doc_topic_
                ally = np.array(getLabels(lns))
                (labelIndex, noLabelIndex) = getLabelIndex(lns)
                X = allX[labelIndex]
                y = ally[labelIndex]
             
                nT = p['nTopics']
                np.save('./lda_data/t%d_nT%d_allX.npy' % (t, nT), allX)
                np.save('./lda_data/t%d_nT%d_labelX.npy' % (t, nT), X)
                np.save('./lda_data/t%d_nT%d_unlabelX.npy' % (t, nT), allX[noLabelIndex])
                np.save('./lda_data/t%d_nT%d_y.npy' % (t, nT), y)

                #expLog = RunExp.runTask(X, y, topicVolcDict, newsIdList[t], 'SelfTrainTest', p, topicId=t, **setting)
            #with open('%s_SelfTrainTest_topic%d.pickle' % (taskName, t), 'w+b') as f:
            #    pickle.dump(expLog, f)

