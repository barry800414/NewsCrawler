
import sys
import math
import heapq
import codecs

import numpy as np
from scipy.sparse import csr_matrix, linalg, identity
from scipy.spatial.distance import pdist, cosine
from scipy.io import mmwrite, mmread
from Volc import *

# read word vector(text file) from word2vec tool
def readWordVector(filename):
    volc = Volc()
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        line = f.readline()
        entry = line.strip().split(' ')
        volcNum = int(entry[0])
        dim = int(entry[1])
        vectors = list()
        i = 0
        while True:
            try:
                line = f.readline()
                if not line:
                    break
            except Exception as e:
                print('\nAt line %d' % i, e)
                line = f.readline()
                volcNum = volcNum - 1
                i = i + 1
                continue
            
            entry = line.strip().split(' ')
            if len(entry) != dim + 1:
                print(line)
                print(len(entry))
            assert len(entry) == dim + 1
            assert entry[0].strip() not in volc
            volc.addWord(entry[0].strip())
            vector = list()
            for j in range(1, len(entry)):
                vector.append(float(entry[j]))
            vectors.append(vector)
            i = i + 1
            if (i+1) % 10000 == 0:
                print('%cProgress: (%d/%d)' % (13, i+1, volcNum), end='', file=sys.stderr)
        print('', file=sys.stderr)
    assert len(volc) == len(vectors)
    vectors = np.array(vectors, dtype=np.float64)
    return (volc, vectors)


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
    if method == 'TopK':
        assert methodValue > 0.0
        num = int(nWords * methodValue)
    elif method == 'Percent':
        assert methodValue <= 1. and methodValue >= 0.0
        num = round(math.pow(nWords, 2) * methodValue)
    return num

# get list of selected edges by given method
def getEdgeList(dist, nWords, method, methodValue):
    if method in ['TopK', 'Percent']:
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
            print('%cProgress:(%d/%d)' % (13, i+1, step), end='', file=sys.stderr)
        print('', file=sys.stderr)
    return F

# filter the values in csr_matrix by given threshold
def filterByThreshold(V, threshold, smallerBeFiltered=True):
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
            if (smallerBeFiltered and value >= threshold) or (not smallerBeFiltered and value <= threshold):
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
    assert selectMethod in ['TopK', 'Threshold']
    print('Word propagation ... ', file=sys.stderr)
    F = wordProp(S, W, beta, step)
    print('Selecting words ...', file=sys.stderr)
    if selectMethod == 'TopK':
        assert selectValue >= 0.0
        assert nWordsPerDoc is not None and len(nWordsPerDoc) == F.shape[0]
        kList = [round(selectValue * nWords) for nWords in nWordsPerDoc]
        F = selectTopK(F, kList)
    elif selectMethod == 'Threshold':
        assert selectValue >= 0.0
        F = filterByThreshold(F, selectValue)
    return F



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

def filterByVolc(X, XVolc, inVolc):
    indexList = list()
    newVolc = Volc()
    for i in range(0, len(inVolc)):
        w = inVolc.getWord(i)
        if w in XVolc:
            indexList.append(XVolc[w])
            newVolc.addWord(w)
    newX = X[indexList]
    return (newX, newVolc)

def test(W, volc):

    import time
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
    if len(sys.argv) < 6:
        print('Usage:', sys.argv[0], 'WordVectorFile SelectMethod value OutWordMatrix OutVolcFile [inVolcFile]', file=sys.stderr)
        print('\t- WordVectorFile: word vector file from word2vec tool', file=sys.stderr)
        print('\t- SelectMethod: method of selecting edges (TopK: N*#word, Percent: p*#word^2, Threshold: threshold of cosine similarity)', file=sys.stderr)
        exit(-1)

    WVFile = sys.argv[1]
    method = sys.argv[2]
    methodValue = float(sys.argv[3])
    wordGraphFile = sys.argv[4]
    volcFile = sys.argv[5]
    
    (volc, X) = readWordVector(WVFile)
    if len(sys.argv) == 7:
        print('filter by volc ...', file=sys.stderr)
        inVolcFile = sys.argv[6]
        inVolc = Volc()
        inVolc.load(inVolcFile)
        (newX, newVolc) = filterByVolc(X, volc, inVolc)
    else:
        newX = X
        newVolc = volc

    print('volc size:', len(newVolc), file=sys.stderr)
    W = buildWordMatrix(newX, method, methodValue)
    #print(W)
    #printWordGraph(W, volc)
    
    # volc & W is the word graph
    mmwrite(wordGraphFile, W)
    newVolc.save(volcFile)


