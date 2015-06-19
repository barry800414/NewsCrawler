
import sys
import math
import heapq
import time

import numpy as np
from scipy.sparse import csr_matrix, linalg, identity
from scipy.spatial.distance import pdist, cosine
from ConvertWordVector import *

## ----------- For building word-word transition matrix from word vector matrix ---------- ##

# method: method to selecting edges
# return: W: word-word transition matrix
def buildWordMatrix(vectorList, method, methodValue):
    nWords = len(vectorList)
    # convert to ndarray 
    print('Converting word vector array ...', file=sys.stderr)
    X = np.array(vectorList)       
    # calculate cosine distance of each two row vector (1 - cosine(v1, v2))
    print('Calculating distance(similarity) of each pair of word vector ...', file=sys.stderr)
    dist = pdist(X, 'cosine')
    # get list of selected edges by given method
    print('Selecting edges ...', file=sys.stderr)
    edgeList = getEdgeList(dist, nWords, method, methodValue)
    # build word matrix 
    print('building word matrix(CSR Matrix) ...', file=sys.stderr)
    W = genWordMatrix(edgeList, nWords)
    return W

def __calcCosDist(X, i, nWords):
    for j in range(i+1, nWords):
        scipy.spatial.distance.cosine(u, v)[source]

def getTargetEdgeNum(nWords, method, methodValue):
    if method == 'TopN':
        assert methodValue > 0.0
        num = int(nWords * methodValue)
    elif method == 'Percent':
        assert methodValue <= 1. and methodValue >= 0.0
        num = round(math.pow(nWords, 2) * methodValue)
    return num

# get list of selected edges by given method
def getEdgeList(dist, nWords, method, methodValue):
    if method in ['TopN', 'Percent']:
        targetNum = getTargetEdgeNum(nWords, method, methodValue)
        edgeList = list()
        index = 0
        for i in range(0, nWords):
            for j in range(i+1, nWords):
                sim = 1. - dist[index] + 1.  # mapping to [0, 2]
                if len(edgeList) >= targetNum:
                    if sim > edgeList[0][0]:
                        heapq.heappop(edgeList)
                        heapq.heappush(edgeList, (sim, (i, j)))
                else:
                    heapq.heappush(edgeList, (sim, (i, j)))
                index += 1
    elif method in ['Threshold']:
        edgeList = list()
        index = 0
        for i in range(0, nWords):
            for j in range(i+1, nWords):
                sim = 1. - dist[index] + 1.  #mapping to [0, 2]
                if sim > methodValue:
                    edgeList.append((sim, (i, j)))
                index += 1
    return edgeList

# generate word-word transition csr_matrix from edgeList
def genWordMatrix(edgeList, nWords):
    rowSum = [0.0 for i in range(0, nWords)]
    for sim, (i, j) in edgeList:
        rowSum[i] += sim
        rowSum[j] += sim
    data = list()
    rows = list()
    cols = list()
    for sim, (i, j) in edgeList:
        data.append(sim / rowSum[i])
        data.append(sim / rowSum[j])
        rows.append(i)
        rows.append(j)
        cols.append(j)
        cols.append(i)

    W = csr_matrix((data, (rows, cols)), shape=(nWords, nWords))
    return W

def printWordGraph(W, volc):
    (rowNum, colNum) = W.shape
    colIndex = W.indices
    rowPtr = W.indptr
    data = W.data

    # traverse whole matrix 
    for ri in range(0, rowNum):
        print(volc.getWord(ri, usingJson=False), end=': ')
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            print(volc.getWord(ci, usingJson=False), end=', ')
        print('')


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
    return F

# filter the values in csr_matrix by given threshold
def filterByThreshold(V, threshold, smaller=True):
    (rowNum, colNum) = V.shape
    colIndex = V.indices
    rowPtr = V.indptr
    data = V.data
    
    # traverse whole matrix to filter values
    rows = list()
    cols = list()
    newData = list()
    nowPos = 0
    for ri in range(0, rowNum):
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            if (smaller and value >= threshold) or (not smaller and value <= threshold):
                rows.append(ri)
                cols.append(ci)
                newData.append(data[nowPos])
            nowPos += 1
    newV = csr_matrix((newData, (rows, cols)), shape=V.shape)
    return newV

# select best K values of each row in csr_matrix
def selectTopK(V, kList, largerIsBetter=True):
    (rowNum, colNum) = V.shape
    assert rowNum == len(kList)
    colIndex = V.indices
    rowPtr = V.indptr
    data = V.data
    
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

# print word and its value in feature vector
def printFeatureVector(V, volc, sortByValue=True, reverse=True):
    (rowNum, colNum) = V.shape
    assert rowNum == 1
    colIndex = V.indices
    rowPtr = V.indptr
    data = V.data

    # traverse whole matrix 
    cwvList = list()
    nowPos = 0
    for ri in range(0, rowNum):
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            cwvList.append((ci, volc.getWord(ci, usingJson=False), value))
            nowPos += 1
    if sortByValue:
        cwvList.sort(key=lambda x:x[2], reverse=reverse)

    for ci, w, v in cwvList:
        print(ci, w, v)

def test(W, volc):
    # test case
    data = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    rows = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    cols = [8, 21, 37, 43, 51, 54, 67, 68, 69, 70, 74, 87]
    S = csr_matrix((data, (rows, cols)), shape=(1, len(volc)))
    
    printFeatureVector(S, volc)
    print('step:-1, time:', end='')
    s = time.time()
    F = wordProp(S, W, 0.7, step=-1)
    e = time.time()
    print(e-s)
    printFeatureVector(F, volc)
    
    print('step: 10, time:', end='')
    s = time.time()
    F = wordProp(S, W, 0.7, step=10)
    e = time.time()
    print(e-s)
    printFeatureVector(F, volc)
    
    print('FilteredByThreshold')
    printFeatureVector(filterByThreshold(F, 0.5), volc)
    print('Selecting topN')
    printFeatureVector(selectTopK(F, [5 for i in range(0, F.shape[0])]), volc)
    
    print('Test sparsity when multiplying W multiple times')
    P = identity(W.shape[0])
    for i in range(0, 30):
        P = P * W
        print(i+1, float(len(P.data)) / (P.shape[0] * P.shape[1]), sep=': ')


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:', sys.argv[0], 'WordVectorFile SelectMethod value [OutWordMatrix OutVolcFile]', file=sys.stderr)
        print('\t- WordVectorFile: word vector file from word2vec tool', file=sys.stderr)
        print('\t- SelectMethod: method of selecting edges (TopN: N*#word, Percent: p*#word^2, Threshold: threshold of cosine similarity)', file=sys.stderr)
        exit(-1)

    WVFile = sys.argv[1]
    method = sys.argv[2]
    methodValue = float(sys.argv[3])
   
    (volc, vectorList) = readWordVector(WVFile)
    W = buildWordMatrix(vectorList, method, methodValue)
    #print(W)
    #printWordGraph(W, volc)
    
    # volc & W is the word graph
    if len(sys.argv) == 6:
        wordGraphFile = sys.argv[4]
        volcFile = sys.argv[5]
        np.save(wordGraphFile, W)
        volc.save(volcFile)


