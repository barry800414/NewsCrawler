
import sys
import math

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC

from misc import *



# print Coefficients in classifier
# clf: classifier
# volc: volc -> index (dict) for each column (feature)
# classMap: class-> text (dict)
def printCoef(clf, volc, wVolc, classMap, sort=False, reverse=True, outfile=sys.stdout):
    supportCoef = [MultinomialNB, LogisticRegression, LinearSVC]
    if type(clf) in supportCoef:
        print('Coefficients:', file=outfile)
        
        coef = clf.coef_
        cNum = coef.shape[0] # class number
        cList = clf.classes_
        fNum = coef.shape[1] # feature number
        print('featureNum:', fNum)
        print('volc size:', len(volc))
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
            print('Class %s' % classMap[cList[ci]], end=',', file=outfile)
        print('', file=outfile)

        for ri in range(0, fNum):
            for ci in range(0, cNum):
                (wIndex, value) = cValues[ci][ri]
                print(volc.getWord(wIndex), value, sep=',', end=',', file=outfile)
            print('', file=outfile)
        
        if wVolc != None:
            printVolc(wVolc, outfile=outfile)
    else:
        return 

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

# X is CSR-Matrix
def printXY(X, y, yPredict, volc, wVolc, classMap, outfile=sys.stdout):
    assert X.shape[1] == len(volc)
    
    (rowNum, colNum) = X.shape
    colIndex = X.indices
    rowPtr = X.indptr
    data = X.data
    nowPos = 0
    
    #sumOfCol = [0.0 for i in range(0, colNum)]
    docF = [0 for i in range(0, colNum)]
    print('label, predict', file=outfile)
    for ri in range(0, rowNum):
        print('%s, %s, ' % (classMap[y[ri]], classMap[yPredict[ri]]), end=',', file=outfile)
        for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
            value = data[nowPos]
            word = volc.getWord(ci)
            print('(%d/%s):%.2f' % (ci, word, value), end=',', file=outfile)
            if math.fabs(value) > 1e-15:
                docF[ci] += 1
            nowPos += 1
        print('', file=outfile)

    for ci in range(0, colNum):
        word = volc.getWord(ci)
        print('(%d/%s):%.2f' % (ci, word, docF[ci]), file=outfile)

    if wVolc != None:
        printVolc(wVolc, outfile=outfile)

    #print('', file=outfile)

def printVolc(volc, outfile=sys.stdout):
    print('Volcabulary:', file=outfile)
    for i in range(0, len(volc)):
        print(i, volc.getWord(i), sep=',', file=outfile)


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'pickle coeff_CSV X_csv', file=sys.stderr)
        exit(-1)

    import pickle
    
    pickleFile = sys.argv[1]
    coeffCSV = sys.argv[2]
    XCSV = sys.argv[3]

    with open(pickleFile, 'r+b') as f:
        p = pickle.load(f)

    clf = p['clf']
    params = p['params']
    volc = p['volc']
    wVolc = p['wVolc']
    result = p['result']

    with open(coeffCSV, 'w') as f:
        print(clf, file=f)
        print('Parameters:', toStr(params), sep=',', file=f) 
        printCoef(clf, volc, wVolc, i2Label, sort=True, reverse=True, outfile=f)

    '''
    with open(XCSV, 'w') as f:
        print(clf, file=f)
        print('Parameters:', toStr(params), sep=',', file=f) 
        printCSRMatrix(X, volc, outfile=f)
    '''

    with open(XCSV, 'w') as f:
        print(clf, file=f)
        print('Parameters:', toStr(params), file=f)
        print('Results:', result, file=f)
        print('Training Data:', file=f)
        X = p['data']['XTrain']
        y = p['data']['yTrain']
        yPredict = clf.predict(X)
        printXY(X, y, yPredict, volc, wVolc, i2Label, outfile=f)
        
        print('Testing Data:', file=f)
        X = p['data']['XTest']
        y = p['data']['yTest']
        yPredict = clf.predict(X)
        printXY(X, y, yPredict, volc, wVolc, i2Label, outfile=f)
