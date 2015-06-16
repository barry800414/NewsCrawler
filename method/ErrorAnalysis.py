
import sys
import math
import pickle

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix
from misc import *

# depricated
def printIntercept(clf, classMap, outfile=sys.stderr):
    supportIntercept = [MultinomialNB, LogisticRegression]
    if type(clf) in supportIntercept:
        print('Intercept (class bias):', file=outfile)
        for ci in range(0, len(clf.classes_)):
            print('Class %s' % classMap[clf.classes_[ci]], clf.intercept_[ci], sep=',', file=outfile)
    else:
        return 

# depricated
def printDenseMatrix(m, volc, outfile=sys.stdout):
    assert m.shape[1] == len(volc)
    
    for i in range(0, len(volc)):
        print(volc.getWord(i), end=',', file=outfile)
    print('', file=outfile)
    for row in m:
        for i in range(0, m.shape[1]):
            print(row[i], end=',', file=outfile)
        print('', file=outfile)

# depricated
def printCSRMatrix(m, volc, outfile=sys.stdout):
    assert m.shape[1] == len(volc)
    
    (rowNum, colNum) = m.shape
    colIndex = m.indices
    rowPtr = m.indptr
    data = m.data
    nowPos = 0
    
    sumOfCol = [0.0 for i in range(0, colNum)]
    for ri in range(0, rowNum):
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            word = volc.getWord(ci)
            print('(%d/%s):%.2f' % (ci, toStr(word, ensure_ascii=False), value), end=',', file=outfile)
            sumOfCol[ci] += value
            nowPos += 1
        print('', file=outfile)

    for ci in range(0, colNum):
        word = volc.getWord(ci)
        print('(%d/%s):%.2f' % (ci, toStr(word, ensure_ascii=False), sumOfCol[ci]), file=outfile)
    #print('', file=outfile)

# print Coefficients in classifier
# clf: classifier
# volc: volc -> index (dict) for each column (feature)
# classMap: class-> text (dict)
def printCoef(clf, volcDict, classMap, sort=False, reverse=True, outfile=sys.stdout):
    supportCoef = [MultinomialNB, LogisticRegression, LinearSVC]
    if type(clf) in supportCoef:
        print('Coefficients:', file=outfile)
        
        coef = clf.coef_
        cNum = coef.shape[0] # class number
        cList = clf.classes_
        fNum = coef.shape[1] # feature number
        print('featureNum:', fNum)
        print('main volc size:', getMainVolcSize(volcDict))
        # for each class, sort the vector
        cValues = list()
        for ci in range(0, cNum):
            values = [(i, v) for i, v in enumerate(coef[ci])]
            if sort:
                values.sort(key=lambda x:x[1], reverse=reverse)
            else:
                values = [(i, v) for i, v in enumerate(coef[ci])]
            cValues.append(values)

        for ci in range(0, cNum):
            print('Class %s' % classMap[cList[ci]], end=',,', file=outfile)
        print('', file=outfile)

        for ri in range(0, fNum):
            for ci in range(0, cNum):
                (wIndex, value) = cValues[ci][ri]
                print('(%d/%s)' % (wIndex, getWord(volcDict, wIndex)), value, sep=',', end=',', file=outfile)
            print('', file=outfile)
        
    else:
        return 



# X is CSR-Matrix
def printXY(X, y, yPredict, volcDict, classMap, newsIdList=None, outfile=sys.stdout):
    assert X.shape[1] == getMainVolcSize(volcDict)
    
    (rowNum, colNum) = X.shape
    colIndex = X.indices
    rowPtr = X.indptr
    data = X.data
    nowPos = 0
    
    print('ConfusionMaxtrix: %s' % classMap, file=outfile)
    print(confusion_matrix(y, yPredict), file=outfile)
    #sumOfCol = [0.0 for i in range(0, colNum)]
    docF = [0 for i in range(0, colNum)]
    if newsIdList != None:
        print('news id', end=',', file=outfile)
    print('label, predict', file=outfile)
    for ri in range(0, rowNum):
        if newsIdList != None:
            print(newsIdList[ri], end=',', file=outfile)

        print(classMap[y[ri]], classMap[yPredict[ri]], sep=',', end='', file=outfile)
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            word = getWord(volcDict, ci)
            print('(%d/%s):%.2f' % (ci, word, value), end=',', file=outfile)
            if math.fabs(value) > 1e-15:
                docF[ci] += 1
            nowPos += 1
        print('', file=outfile)

    print('Document Frequency:', file=outfile)
    for ci in range(0, colNum):
        word = getWord(volcDict, ci)
        print('(%d/%s):%.2f' % (ci, word, docF[ci]), file=outfile)

    #print('', file=outfile)

def printVolc(volc, outfile=sys.stdout):
    print('Volcabulary:', file=outfile)
    for i in range(0, len(volc)):
        print(i, volc.getWord(i), sep=',', file=outfile)

def getWord(volcDict, index):
    if type(volcDict) == dict:
        return volcDict['main'].getWord(index, maxLength=15)
    elif type(volcDict) == list:
        volcSize = [len(v['main']) for v in volcDict]
        assert index < sum(volcSize)

        for i in range(0, len(volcSize)):
            if index >= volcSize[i]:
                index = index - volcSize[i]
            else:
                return volcDict[i]['main'].getWord(index, maxLength=15)

def getMainVolcSize(volcDict):
    if type(volcDict) == dict:
        return len(volcDict['main'])
    elif type(volcDict) == list:
        return sum([len(v['main']) for v in volcDict])

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'pickle outFilePrefix', file=sys.stderr)
        exit(-1)

    
    pickleFile = sys.argv[1]
    outFilePrefix = sys.argv[2]

    with open(pickleFile, 'r+b') as f:
        p = pickle.load(f)
    
    log0 = p['logList'][0]
    clf = log0['clf']
    params = p['params']
    volcDict = p['volcDict']

    with open(outFilePrefix + '_coeff.csv', 'w') as f:
        print(clf, file=f)
        print('Parameters:', toStr(params), sep=',', file=f) 
        printCoef(clf, volcDict, i2Label, sort=True, reverse=True, outfile=f)

    X = p['data']['X']
    y = p['data']['y']
    trainIndex = log0['split']['trainIndex']
    testIndex = log0['split']['testIndex']
    valScore = log0['valScore']
    testScore = log0['testScore']
    newsIdList = p['newsIdList']

    with open(outFilePrefix + '_X.csv', 'w') as f:
        print(clf, file=f)
        print('Parameters:', toStr(params), file=f)
        print('valScore:', valScore, file=f)
        print('testScore:', testScore, file=f)
        print('Training Data:', file=f)
        XTrain = X[trainIndex]
        yTrain = y[trainIndex]
        newsIds = [newsIdList[i] for i in trainIndex]
        yTrainPredict = log0['predict']['yTrainPredict']
        printXY(XTrain, yTrain, yTrainPredict, volcDict, i2Label, newsIdList=newsIds, outfile=f)
        
        print('Testing Data:', file=f)
        XTest = X[testIndex]
        yTest = y[testIndex]
        yTestPredict = log0['predict']['yTestPredict']
        newsIds = [newsIdList[i] for i in testIndex]
        printXY(XTest, yTest, yTestPredict, volcDict, i2Label, newsIdList=newsIds, outfile=f)

