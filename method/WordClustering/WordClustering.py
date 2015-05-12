
import sys
import math

import numpy as np
from sklearn.cluster import KMeans, MiniBatchKMeans, AgglomerativeClustering

from misc import *
from Volc import Volc
import WordTag 

'''
This module implements the function for word clustering.
Each word is represented by a vector, which is from certain
latent model(e.g. LSA, LDA, RNN ... )
The method of word clustering includes K-means ...
'''

def wordClustering(X, method, n_clusters, params):
    if method == 'KMeans':
        est = KMeans(n_clusters=n_clusters, n_jobs=-1, **params)
    elif method == 'MiniBatchKMeans':
        est = MiniBatchKMeans(n_clusters=n_clusters, **params)
    elif method == 'AgglomerativeClustering':
        est = MiniBatchKMeans(n_clusters=n_clusters, **params)

    labels = est.fit_predict(X)
    #print(len(labels))
    return labels


def getWordCluster(labels, volc):
    clusters = dict()
    for i, label in enumerate(labels):
        if label not in clusters:
            clusters[label] = list()
        clusters[label].append(volc.getWord(i))
    return clusters

def printWordCluster(clusters, outfile=sys.stdout):
    for key, words in sorted(clusters.items(), key=lambda x:x[0]):
        for w in words:
            print(w, end=',', file=outfile)
        print('', file=outfile)

def printWordClusterAsVolc(clusters, outfile=sys.stdout):
    for key, words in sorted(clusters.items(), key=lambda x:x[0]):
        for w in words:
            print(w, key, sep=':', file=outfile)

def filterByWord(X, volc, wordSet):
    # some of words in wordSet may not be in volc(because less 5 times words 
    # are removed)
    indexList = sorted(list(set([volc[w] for w in wordSet if w in volc])))
    newX = X[indexList]
    
    oldNewMapping = { oldI:newI for newI, oldI in enumerate(indexList) }
    newVolc = Volc()
    for w in wordSet:
        if w in volc:
            newVolc[w] = oldNewMapping[volc[w]]
            #if not np.array_equal(newX[oldNewMapping[volc[w]]],X[volc[w]]):
            #    print('fail')

    #print(newX.shape, len(newVolc))
    return (newX, newVolc)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage:', sys.argv[0], 'WordVector volcFile nCluster outWordClusterPrefix [WordTagFile]', file=sys.stderr)
        exit(-1)

    wordVectorFile = sys.argv[1]
    volcFile = sys.argv[2]
    nCluster = int(sys.argv[3])
    print('nCluster:', nCluster, file=sys.stderr)
    wordClusterFile = sys.argv[4]
    tagWord = None

    print('Loading word vector matrix ...', file=sys.stderr)
    WX = np.load(wordVectorFile)
    print(WX.shape)
    print('Loading volcabulary ...', file=sys.stderr)
    volc = Volc()
    volc.load(volcFile)

    if len(sys.argv) == 6:
        # one word should have only one POS tag (most frequent)
        wordTagFile = sys.argv[5]
        with open(wordTagFile, 'r') as f:
            (wordTag, tagWord) = WordTag.loadWordTag(f)
        allowedPOS = set(['NN', 'NR', 'VV', 'VA', 'AD', 'JJ'])

    if tagWord == None:
        print('K-means clustering ...', file=sys.stderr)
        labels = wordClustering(WX, 'KMeans', nCluster, {})
    
        clusters = getWordCluster(labels, volc)
        with open(wordClusterFile + '.volc', 'w') as f, open(wordClusterFile + '.txt', 'w') as f2:
            printWordClusterAsVolc(clusters, outfile=f)
            printWordCluster(clusters, outfile=f2)
    else:
        print('K-means clustering ...', file=sys.stderr)
        nWords = sum([len(wordSet) for tag, wordSet in tagWord.items() if tag in allowedPOS])
        nClusterEachTag = { tag: math.ceil(len(tagWord[tag])*nCluster/nWords) for tag in tagWord.keys() if tag in allowedPOS }
        print(nClusterEachTag)
        with open(wordClusterFile + '.volc', 'w') as f, open(wordClusterFile + '.txt', 'w') as f2:
            for tag, wordSet in tagWord.items():
                if tag not in allowedPOS:
                    continue
                print('clustering for tag %s words (%d words to %d clusters)... ' % (
                    tag, len(wordSet), nClusterEachTag[tag]), file=sys.stderr)
                (newX, newVolc) = filterByWord(WX, volc, wordSet)
                if newX.shape[0] == 0:
                    continue
                labels = wordClustering(newX, 'KMeans', nClusterEachTag[tag], {})
                clusters = getWordCluster(labels, newVolc)
                printWordClusterAsVolc(clusters, outfile=f)
                print('Tag: %s' % (tag), file=f2)
                printWordCluster(clusters, outfile=f2)
