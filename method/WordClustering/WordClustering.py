
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
    print(len(labels))
    return labels


def getWordCluster(labels, rVolc):
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
    # are removed
    indexList = sorted(list(set([volc[w] for w in wordSet if w in volc])))
    newX = X[indexList]
    oldNewMapping = { oldI:newI for newI, oldI in enumerate(indexList) }
    newVolc = Volc()
    for w in wordSet:
        if w in volc:
            newVolc[w] = oldNewMapping[volc[w]]
    return (newX, newVolc)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print('Usage:', sys.argv[0], 'WordVector volcFile nCluster outWordCluster [WordTagFile]', file=sys.stderr)
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

    if tagWord == None:
        print('K-means clustering ...', file=sys.stderr)
        labels = wordClustering(WX, 'KMeans', nCluster, {})
    
        clusters = getWordCluster(labels, volc)
        with open(wordClusterFile, 'w') as f:
            #printWordClusterAsVolc(clusters, outfile=f)

    else:
        print('K-means clustering ...', file=sys.stderr)
        nWords = sum([len(wordSet) for wordSet in tagWord.values()])
        nClusterEachTag = { tag: math.ceil(len(tagWord[tag])*nCluster/nWords) for tag in tagWord.keys() }
        print(nClusterEachTag)
        with open(wordClusterFile, 'w') as f:
            for tag, wordSet in tagWord.items():
                print('clustering for tag %s words ...' % tag, file=sys.stderr)
                (newX, newVolc) = filterByWord(WX, volc, wordSet)
                if newX.shape[0] == 0:
                    continue
                labels = wordClustering(newX, 'KMeans', nClusterEachTag[tag], {})
                clusters = getWordCluster(labels, newVolc)
                print('Tag: %s' % (tag), file=f)
                printWordCluster(clusters, outfile=f)

