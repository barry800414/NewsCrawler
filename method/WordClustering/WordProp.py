
import sys
import math
import heapq
import json 

import numpy as np
from scipy.sparse import csr_matrix, linalg, identity
from scipy.io import mmwrite, mmread
from Volc import *

## ----------- For using word-word transition matrix ---------- ##

# S: 1xN or MxN sparse matrix : bag-of-word vector(1xN)/ bag-of-word vector of M doc (MxN)
# W: NxN sparse matrix : word-word transition prob
# beta: damping factor
# step: number of steps to diffuse word information
def wordProp(S, W, beta, step):
    assert S.shape[1] == W.shape[0] and W.shape[0] == W.shape[1]
    assert step == -1 or step >= 0
    nWords = S.shape[1]
    if step == -1: # diffuse infinite steps
        I_AW = (identity(nWords) - beta * W).tocsc()
        F = S*linalg.inv(I_AW)
    else:
        # Question: why not store W^K directly ? => memory consideration
        sw = S # s*w*beta
        F = S # final word matrix
        for i in range(0, step):
            sw = beta * sw * W
            F = F + sw
            print('%cProgress:(%d/%d)' % (13, i+1, step), end='', file=sys.stderr)
        print('', file=sys.stderr)
    return F

# filter the values in csr_matrix by given threshold
def filterByThreshold(V, threshold, smallerBeFiltered=True):
    (rowNum, colNum) = V.shape
    (colIndex, rowPtr, data) = V.indices, V.indptr, V.data
    
    # traverse whole matrix to filter values
    rows = list()
    cols = list()
    newData = list()
    nowPos = 0
    for ri in range(0, rowNum):
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            if (smallerBeFiltered and value >= threshold) or (not smallerBeFiltered and value <= threshold):
                rows.append(ri)
                cols.append(ci)
                newData.append(data[nowPos])
            nowPos += 1
    newV = csr_matrix((newData, (rows, cols)), shape=V.shape)
    return newV

# select best K values of each row in csr_matrix
def selectTopKEachRow(V, kList, largerIsBetter=True):
    (rowNum, colNum) = V.shape
    assert rowNum == len(kList)
    (colIndex, rowPtr, data) = V.indices, V.indptr, V.data
    
    # traverse whole matrix to filter values
    rows = list()
    cols = list()
    newData = list()
    nowPos = 0
    # for each row, select k best values
    for ri in range(0, rowNum):
        heap = list()
        k = kList[ri]
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            if len(heap) >= k: # heap is full
                if (largerIsBetter and value > heap[0][0]) or (not largerIsBetter and value < heap[0][0]):
                    heapq.heappop(heap)
                    heapq.heappush(heap, (value, (ri, ci)))
            else:
                heapq.heappush(heap, (value, (ri, ci)))
            nowPos += 1
        
        for v, (i, j) in heap:
            rows.append(i)
            cols.append(j)
            newData.append(v)

    newV = csr_matrix((newData, (rows, cols)), shape=V.shape)
    return newV

# select best K edges from whole matrix
def selectTopK(V, edgeNum, largerIsBetter=True):
    (rowNum, colNum) = V.shape
    (colIndex, rowPtr, data) = V.indices, V.indptr, V.data
    
    rows = list()
    cols = list()
    newData = list()
    nowPos = 0
    heap = list()
    print('#EdgeNum:', edgeNum, file=sys.stderr)
    # for each row, select k best values
    for ri in range(0, rowNum):
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            if len(heap) >= edgeNum: # heap is full
                if (largerIsBetter and value > heap[0][0]) or (not largerIsBetter and value < heap[0][0]):
                    heapq.heappop(heap)
                    heapq.heappush(heap, (value, (ri, ci)))
            else:
                heapq.heappush(heap, (value, (ri, ci)))
            nowPos += 1
        
    for v, (i, j) in heap:
        rows.append(i)
        cols.append(j)
        newData.append(v)

    newV = csr_matrix((newData, (rows, cols)), shape=V.shape)
    return newV


## ----------- For running word graph propagation alorithm completely ---------- ##
# S: 1xN or MxN sparse matrix : bag-of-word vector(1xN)/ bag-of-word vector of M doc (MxN)
# W: NxN sparse matrix : word-word transition prob
# beta: damping factor
# step: number of steps to diffuse word information
# selectMethod: method to select/filter words with low value (TopK, Threshold)
# selectValue: parameter corresponds to selectMethod
# nWordsPerDoc: # words in original feature matrix(for counting expected K for each doc
# return F: feature matrix after word graph propagation
def runWordGraphProp(S, W, beta, step, selectMethod, selectValue, nWordsPerDoc=None):
    assert selectMethod in ['TopK', 'Threshold', 'TopKEachRow', None]
    print('Word propagation ... ', file=sys.stderr)
    F = wordProp(S, W, beta, step)
    print('Selecting words ...', file=sys.stderr)
    if selectMethod == 'TopKEachRow':
        assert selectValue >= 0.0
        assert nWordsPerDoc is not None and len(nWordsPerDoc) == F.shape[0]
        kList = [round(selectValue * nWords) for nWords in nWordsPerDoc]
        F = selectTopKEachRow(F, kList)
    elif selectMethod == 'TopK':
        edgeNum = round(selectValue * F.shape[0])
        F = selectTopK(F, edgeNum)
    elif selectMethod == 'Threshold':
        assert selectValue >= 0.0
        F = filterByThreshold(F, selectValue)
    return F

def loadWordGraphFromConfig(config, topicSet):
    files = dict() # prevent repeated loading (filename -> wordgraph
    if config == None:
        topicWordGraph = { t:None for t in topicSet }
        topicWordGraph['All'] = None
        topicVolcDict = { t:None for t in topicSet }
        topicVolcDict['All'] = None
        wgParams = { t:None for t in topicSet }
        wgParams['All'] = None
    else:
        topicWordGraph = dict()
        topicVolcDict = dict()
        wgParams = dict()
        for topic, topicConfig in config.items():
            try: topic = int(topic)
            except: assert topic == 'All'
            
            # params
            wgParams[topic] = topicConfig['params']

            # word graph file
            filename = topicConfig['filename']
            if filename in files:
                topicWordGraph[topic] = files[filename]
            else:
                wordGraph = mmread(filename).tocsr() # a csr_matrix
                files[filename] = wordGraph
                topicWordGraph[topic] = wordGraph
            
            # volc
            volcDict = dict()
            for name, filename in topicConfig['volcFile'].items():
                v = Volc()
                v.load(filename)
                v.lock()
                volcDict[name] = v
            topicVolcDict[topic] = volcDict

    return (topicWordGraph, topicVolcDict, wgParams)

def getAdjList(F, allowedSet=None, volc=None):
    adjList = dict()
    if volc is not None:
        assert F.shape[0] == len(volc)
    (rowNum, colNum) = F.shape
    (colIndex, rowPtr, data) = F.indices, F.indptr, F.data
    nowPos = 0
    for ri in range(0, rowNum):
        fromW = volc.getWord(ri, usingJson=False) if volc is not None else ri
        if allowedSet is not None and ri not in allowedSet:
            continue
        adjList[fromW] = list()
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            toW = volc.getWord(ci, usingJson=False) if volc is not None else ci
            value = data[nowPos]
            adjList[fromW].append((toW, value))
            nowPos += 1
    return adjList

def saveAdjList(adjList, outfile):
    for fromW, wList in adjList.items():
        print(fromW, end=':', file=outfile)
        for toW, value in wList:
            print(' %s:%f' % (toW, value), end='', file=outfile)
        print('', file=outfile)

def loadAdjList(infile):
    adjList = dict()
    for line in infile:
        entry = line.strip().split(' ')
        assert len(entry) >= 1
        fromW = entry[0][0:-1].strip()
        adjList[frowW] = list()
        for i, e in entry[1:]:
            (w,v) = e.split(':')
            v = float(v)
            adjList[fromW].append((w, v))
    return adjList

if __name__ == '__main__':
    if len(sys.argv) < 9:
        print('Usage:', sys.argv[0], 'InWordMatrix InVolcFile beta step method value OutAdjFile OutMtxFile', file=sys.stderr)
        print('\t- InWordMatrix: sparse word-word transition matrix (.mtx)', file=sys.stderr)
        print('\t- method: to select edges when generating adj list (TopKEachRow: up to N words each row, TopK: top N*#words, Threshold: threshold of cosine similarity, None: do not propagate)', file=sys.stderr)
        exit(-1)

    WFile = sys.argv[1]
    volcFile = sys.argv[2]
    beta = float(sys.argv[3]) # damping factor [0, 1)
    step = int(sys.argv[4]) # number of steps to do word propagation
    method = sys.argv[5]
    value = int(sys.argv[6]) # (topK * #nodes) will be selected
    outAdjFile = sys.argv[7]
    outMtxFile = sys.argv[8]

    # load sparse word-word transition matrix & volcabulary file
    W = mmread(WFile).tocsr() 
    volc = Volc()
    volc.load(volcFile)
    
    # doing propagation
    nWords = len(volc)
    S = identity(nWords)
    if method != 'None':
        F = runWordGraphProp(S, W, beta, step, method, value, nWordsPerDoc=[1 for i in range(0, nWords)])
    else:
        F = runWordGraphProp(S, W, 1.0, 1, None, None)
    
    mmwrite(outMtxFile, F)
    adjList = getAdjList(F, volc=volc)
    with open(outAdjFile, 'w') as f:
        saveAdjList(adjList, f)

    
