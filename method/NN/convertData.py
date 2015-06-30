
import sys
import numpy as np
from scipy.sparse import csr_matrix, vstack
import climate
import theanets

from scipy.io import mmwrite, mmread

from misc import *

def readSVMData(filename, maxDim):
    ydata = list()
    Xdata = list()
    with open(filename, 'r') as f:
        for line in f:
            entry = line.strip().split(' ') 
            ydata.append(int(entry[0]))
            d = dict()
            for e in entry[1:]:
                w,v = e.strip().split(':')
                w = int(w)
                v = float(v)
                d[w] = v
                assert v <= maxDim
            Xdata.append(d)
    # generating csr matrix
    rows = list()   
    cols = list()
    data = list()
    for i, x in enumerate(Xdata):
        for w, v in x.items():
            rows.append(i)
            cols.append(w - 1)
            data.append(v)
    X = csr_matrix((data, (rows, cols)), shape=(len(Xdata), maxDim), dtype=np.float64)
    y = np.array(ydata)
    return X, y


def divideUnlabeledData(X, y):
    topicIndex = dict()
    for i, yi in enumerate(y):
        if yi not in topicIndex:
            topicIndex[yi] = list()
        topicIndex[yi].append(i)
    topicX = dict()
    for t, indexList in topicIndex.items():
        topicX[t] = X[indexList]
    return topicX, sorted(topicIndex.keys())

def divideLabeledData(X, y):
    # original y is not real label
    topicIndex = dict()
    labels = list()
    for i, yi in enumerate(y):
        label = 0 if yi < 0 else 1
        labels.append(label)
        t = abs(yi)
        if t not in topicIndex:
            topicIndex[t] = list()
        topicIndex[t].append(i)
    y = np.array(labels, dtype=np.uint8)
    #y = y.reshape((len(y), -1))
    topicX = dict()
    topicy = dict()
    for t, indexList in topicIndex.items():
        topicX[t] = X[indexList]
        topicy[t] = y[indexList]
    return topicX, topicy, sorted(topicIndex.keys())

# for the data in each topic, reduce the dimension
def prepareData(topiclX, topicUnX, topicList, minCnt=4):
    newTopiclX = dict()
    newTopicUnX = dict()
    topicAllX = dict()
    for t in topicList:
        lX, unX = topiclX[t], topicUnX[t]
        labelNum, unLabelNum = lX.shape[0], unX.shape[0]
        allX = vstack((lX, unX))
        DF = countDFByCSRMatrix(allX)
        allX = shrinkCSRMatrixByDF(allX, DF, minCnt=minCnt)
        lX = allX[0:labelNum]
        unX = allX[labelNum:]
        newTopiclX[t] = lX
        newTopicUnX[t] = unX
        topicAllX[t] = allX
    return (newTopiclX, newTopicUnX, topicAllX)


def splitTrainValTest(X, y, train, val):
    assert train + val < 1.0
    assert X.shape[0] == len(y)
    num = len(y)
    trainNum = int(num * train)
    valNum = int(num * val)
    testNum = num - trainNum - valNum
    trainIndex = range(0, trainNum)
    valIndex = range(trainNum, trainNum + valNum)
    testIndex = range(trainNum + valNum, trainNum + valNum + testNum)
    return (X[trainIndex], y[trainIndex]), (X[valIndex], y[valIndex]), (X[testIndex], y[testIndex])

def dumpData(topic, lX, ly, unX, AllX):
    mmwrite('t%d_labelX.mtx' % (topic), lX)
    np.save('t%d_label.npy' % (topic), ly)
    mmwrite('t%d_unlabelX.mtx' %(topic), unX)
    mmwrite('t%d_allX.mtx' % (topic), AllX)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'unLabeledData labeledData maxDim', file=sys.stderr)
        exit(-1)
 
    climate.enable_default_logging()
    unLabeledDataFile = sys.argv[1]
    labeledDataFile = sys.argv[2]
    maxDim = int(sys.argv[3]) #33876
    print('Reading unlabeledData ...', file=sys.stderr)
    (unX, uny) = readSVMData(unLabeledDataFile, maxDim=maxDim)
    print('Reading labeledData ...', file=sys.stderr)
    (lX, ly) = readSVMData(labeledDataFile, maxDim=maxDim)
    print('Preparing data ...', file=sys.stderr)
    topicUnX, topicList = divideUnlabeledData(unX, uny)
    topiclX, topicly, topicList = divideLabeledData(lX, ly)
    topiclX, topicUnX, topicAllX = prepareData(topiclX, topicUnX, topicList, minCnt=4)

    for t in topicList:
        lX = topiclX[t]
        ly = topicly[t]
        unX = topicUnX[t]
        allX = topicAllX[t]
        print('lX:', lX.shape)
        print('ly:', ly.shape)
        print('unX:', unX.shape)
        print('allX:', allX.shape)
        dumpData(t, lX, ly, unX, allX)
