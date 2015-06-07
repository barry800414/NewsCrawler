
import sys
import math

import numpy as np
from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering

from misc import *
from Volc import Volc
import WordTag
import ConvertWordVector as CWV

'''
This module implements the function for word clustering.
Each word is represented by a vector, which is from certain
latent model(e.g. LSA, LDA, RNN ... )
The method of word clustering includes K-means ...
'''

# doing word clustering by running clustering algorithm on word vector
# X: each row in X is a word vector
def runClustering(X, method, nCluster, params=None):
    if params == None:
        params = {}
    if method == 'KMeans':
        est = KMeans(n_clusters=nCluster, n_jobs=-1, **params)
    elif method == 'MiniBatchKMeans':
        est = MiniBatchKMeans(n_clusters=nCluster, **params)
    elif method == 'AgglomerativeClustering':
        est = MiniBatchKMeans(n_clusters=nCluster, **params)

    labels = est.fit_predict(X)
    #print(len(labels))
    return labels

# if wordSetEachGroup is given, for each word group, do word clustering, 
# and then merge the results of each group. wordSet in each group should 
# be disjointed (a list of set)
def wordClustering(X, volc, method, nCluster, wordSetEachGroup=None, params=None):
    if wordSetEachGroup is None:
        wordSetEachGroup = {'all':set(volc.volc.keys())}

    newXDict = dict()
    newVolcDict = dict()
    totalWordNum = 0
    for name, wordSet in wordSetEachGroup.items():
        wordSet = wordSetEachGroup[name]
        (newX, newVolc) = CWV.filterByWord(X, volc, wordSet)
        if newX.shape[0] == 0:
            #print('No matched words in this group %s' % (name), file=sys.stderr)
            continue
        newXDict[name] = newX
        newVolcDict[name] = newVolc
        totalWordNum += newX.shape[0]
    
    print('#words in each word set:', { name:newX.shape[0] for name, newX in newXDict.items() }, file=sys.stderr)

    # by percentage
    if nCluster <= 1.0:
        nCluster = math.ceil(nCluster * totalWordNum)

    nClusterEachGroup = { name:math.ceil(nCluster * (float(newX.shape[0]) / totalWordNum)) for name, newX in newXDict.items() }
    print('#clusters in each group:', nClusterEachGroup, file=sys.stderr) 

    clusterList = list()
    for name in newXDict.keys():
        newX = newXDict[name]
        newVolc = newVolcDict[name]
        labels = runClustering(newX, 'KMeans', nClusterEachGroup[name], params)
        clusters = getWordCluster(labels, newVolc)
        clusterList.append(clusters)
    return clusterList

def getWordCluster(labels, volc):
    clusters = dict()
    for i, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = list()
        clusters[label].append(volc.getWord(i, usingJson=False))
    return clusters

# print word clusters for human reading
def printWordCluster(clusters, outfile=sys.stdout):
    for key, words in sorted(clusters.items(), key=lambda x:x[0]):
        for w in words:
            print(w, end=',', file=outfile)
        print('', file=outfile)

def printWordClusterList(clusterList, outfile=sys.stderr):
    for clusters in clusterList:
        printWordCluster(clusters, outfile=outfile)

# print word clusters as volcabulary file
def printWordClusterAsVolc(clusters, offset=0, outfile=sys.stdout):
    for key, words in sorted(clusters.items(), key=lambda x:x[0]):
        for w in words:
            print(w, key+offset, sep=':', file=outfile)

def printWordClusterListAsVolc(clusterList, outfile=sys.stdout):
    offset = 0
    for clusters in clusterList:
        printWordClusterAsVolc(clusters, offset=offset, outfile=outfile)
        offset = offset + len(clusters)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage:', sys.argv[0], 'WordVector volcFile nCluster(nClusterPercentage) outWordClusterPrefix [-wt WordTagFile] [-v sentimentLexicon]', file=sys.stderr)
        exit(-1)

    wordVectorFile = sys.argv[1]
    volcFile = sys.argv[2]
    try: nCluster = int(sys.argv[3])
    except:
        try: nCluster = float(sys.argv[3])
        except: exit(-1)
    print('nCluster:', nCluster, file=sys.stderr)
    outFilePrefix = sys.argv[4]
    tagWord = None
    sentiDict = None
    print('Loading word vector matrix ... ', end='', file=sys.stderr)
    WX = np.load(wordVectorFile)
    print(WX.shape, file=sys.stderr)
    # volcabulary file, for mapping index to words
    print('Loading volcabulary ... ', end='', file=sys.stderr)
    volc = Volc()
    volc.load(volcFile)
    print('#words:', len(volc), file=sys.stderr)

    # loading other inputs
    for i in range(5, len(sys.argv)):
        if sys.argv[i] == '-wt' and  len(sys.argv) > i:
            # one word should have only one POS tag (most frequent)
            print('Loading word-tag file ...', file=sys.stderr)
            with open(sys.argv[i+1], 'r') as f:
                (wordTag, tagWord) = WordTag.loadWordTag(f)
        elif sys.argv[i] == '-v' and len(sys.argv) > i:
            # sentiment lexicon file: for grouping words with same sentiment
            print('Loading sentiment lexicon ...', file=sys.stderr)
            sentiDict = readSentiDict(sys.argv[i+1])

    if tagWord is not None:
        allowedPOS = set(['NN', 'NR', 'VV', 'VA', 'AD', 'JJ'])
        tagWordDict = {tag:wordSet for tag, wordSet in tagWord.items() if tag in allowedPOS}

    if sentiDict is not None:
        posWordSet = set([w for w, s in sentiDict.items() if s > 0])
        negWordSet = set([w for w, s in sentiDict.items() if s < 0])
        neutralWordSet = (set(volc.volc.keys()) - posWordSet) - negWordSet
        sentiWordDict = { "positive": posWordSet, "neutral": neutralWordSet, "negative": negWordSet }

    if tagWord is None:
        if sentiDict is None:
            # cluster all words into N cluster
            print('K-means clustering on all words...', file=sys.stderr)
            wordSetEachGroup = None
        else:
            # group words by sentiment lexicon
            wordSetEachGroup = sentiWordDict
    else:
        if sentiDict is None:
            # group words by tag
            wordSetEachGroup = tagWordDict
        else:
            # group words by tag & sentiment lexicon
            wordSetEachGroup = dict()
            for senti, set1 in sentiWordDict.items():
                for tag, set2 in tagWordDict.items():
                    wordSetEachGroup[senti + '_' + tag] = set1 & set2
    
    clusterList = wordClustering(WX, volc, 'KMeans', nCluster, wordSetEachGroup)
    
    print('#clusters in clusterList:', len(clusterList))
    with open(outFilePrefix + '.volc', 'w') as f, open(outFilePrefix + '.txt', 'w') as f2:
        printWordClusterListAsVolc(clusterList, outfile=f)
        printWordClusterList(clusterList, outfile=f2)
