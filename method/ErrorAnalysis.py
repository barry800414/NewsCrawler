
import sys
import math
import pickle

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix, accuracy_score
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
def printCoef(clf, volcDict, classMap, sort=False, reverse=True, wordRank=None, outfile=sys.stdout):
    supportCoef = [MultinomialNB, LogisticRegression, LinearSVC]
    if type(clf) in supportCoef:
        if clf.coef_.shape[0] == 1:
            print('Binary classification')
            __printBinaryCoeff(clf, volcDict, classMap, sort, reverse, wordRank, outfile)
        else:
            __printMultiClassCoeff(clf, volcDict, classMap, sort, reverse, wordRank, outfile)
    else:
        return 


def __printMultiClassCoeff(clf, volcDict, classMap, sort=False, reverse=True, wordRank=None, outfile=sys.stdout):
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


def __printBinaryCoeff(clf, volcDict, classMap, sort=False, reverse=True, wordRank=None, outfile=sys.stdout):
    print('Coefficients:', file=outfile)
    coef = clf.coef_
    cNum = coef.shape[0] # class number
    cList = clf.classes_

    fNum = coef.shape[1] # feature number
    print('featureNum:', fNum)
    print('main volc size:', getMainVolcSize(volcDict))
    # for each class, sort the vector
    cValues = list()
    values = [(i, v) for i, v in enumerate(coef[0])]
    if sort:
        values.sort(key=lambda x:x[1], reverse=reverse)
        middle = int(fNum / 2)
        cValues.append(values[0:middle]) #class 1
        cValues.append(sorted(values[middle:], key=lambda x:x[1], reverse = not reverse)) #class 0
        print('Class %s,, Class %s' % (classMap[1], classMap[0]), file=outfile)
        for ri in range(0, max(len(cValues[0]), len(cValues[1]))):
            for ci in [0, 1]:
                if ri < len(cValues[ci]):
                    (wIndex, value) = cValues[ci][ri]
                    print(genOutStr(wIndex, volcDict, wordRank, value), end=',', file=outfile)
            print('', file=outfile)

    else:
        values = [(i, v) for i, v in enumerate(coef[0])]
        cValues.append(values)
        print('Class %s' % (classMap[1]), file=outfile)
        for ri in range(0, fNum):
            (wIndex, value) = cValues[0][ri]
            print(genOutStr(wIndex, volcDict, wordRank, value), end=',', file=outfile)
            print('', file=outfile)

def genOutStr(wIndex, volcDict, wordRank, value):
    word = getWord(volcDict, wIndex, usingJson=False)
    if wordRank is not None:
        rank = wordRank[word] if word in wordRank else None
        #if rank >= 3483 and rank <= 6986:
        #    return '\033[1;33m(%d / %s / %s)\033[0m, %f' % (wIndex, word, str(rank), value)
        return '(%d / %s / %s), %f' % (wIndex, word, str(rank), value)
    else:
        return '(%d / %s), %f' % (wIndex, word, value)


# X is CSR-Matrix
def printXY(X, y, yPredict, volcDict, classMap, newsIdList=None, outfile=sys.stdout, showWordIndex=False):
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
            word = getWord(volcDict, ci, usingJson=False)
            if showWordIndex:
                print('(%d/%s):%.2f' % (ci, word, value), end=',', file=outfile)
            else:
                print('%s:%.2f' % (word, value), end=',', file=outfile)
            if math.fabs(value) > 1e-15:
                docF[ci] += 1
            nowPos += 1
        print('', file=outfile)

    print('Document Frequency:', file=outfile)
    for ci in range(0, colNum):
        word = getWord(volcDict, ci)
        print('(%d/%s):%.2f' % (ci, word, docF[ci]), file=outfile)

    #print('', file=outfile)

def printCScore(logList, scorerName, y, outfile=sys.stdout):
    for log in logList:
        C = log['param']['C']
        testScore = log['testScore'][scorerName]
        valScore = log['valScore']
        trainIndex = log['split']['trainIndex']
        testIndex = log['split']['testIndex']
        yTrain = y[trainIndex]
        yTrainPredict = log['predict']['yTrainPredict']
        trainScore = accuracy_score(yTrain, yTrainPredict)
        print(C, valScore, trainScore, testScore, file=outfile)

def printLog(log, y, classMap, outfile=sys.stdout):
    clf = log['clf']
    #params = log['params']
    valScore = log['valScore']
    testScore = log['testScore']
    param = log['param']
    print(clf, file=outfile)
    print('Parameters:', toStr(param), file=outfile)
    print('valScore:', valScore, file=outfile)
    print('testScore:', testScore, file=outfile)
    trainIndex = log['split']['trainIndex']
    testIndex = log['split']['testIndex']
    yTrain = y[trainIndex]
    yTest = y[testIndex]
    yTrainPredict = log['predict']['yTrainPredict']
    yTestPredict = log['predict']['yTestPredict']
    print('Training Data ConfusionMaxtrix: %s' % classMap, file=outfile)
    print(confusion_matrix(yTrain, yTrainPredict), file=outfile)
    print('Testing Data ConfusionMaxtrix: %s' % classMap, file=outfile)
    print(confusion_matrix(yTest, yTestPredict), file=outfile)
    print('\n\n', file=outfile)

def printVolc(volc, outfile=sys.stdout):
    print('Volcabulary:', file=outfile)
    for i in range(0, len(volc)):
        print(i, volc.getWord(i), sep=',', file=outfile)

def getWord(volcDict, index, usingJson=False, recursive=True):
    if type(volcDict) == dict:
        word = volcDict['main'].getWord(index, maxLength=15, usingJson=usingJson)
        if recursive:
            return __recursiveGetWord(volcDict, word, usingJson=usingJson)
        else:
            return word
    elif type(volcDict) == list:
        volcSize = [len(v['main']) for v in volcDict]
        assert index < sum(volcSize)

        for i in range(0, len(volcSize)):
            if index >= volcSize[i]:
                index = index - volcSize[i]
            else:
                word = volcDict[i]['main'].getWord(index, maxLength=15, usingJson=usingJson)
                if recursive:
                    return __recursiveGetWord(volcDict, word, usingJson=usingJson)
                else:
                    return word

def __recursiveGetWord(volcDict, word, usingJson=False):
    if type(word) == str:
        return word
    newW = list(word)
    #OLDM
    if 'seed' in volcDict: 
        newW[0] = volcDict['seed'].getWord(word[0], maxLength=15, usingJson=usingJson)
    if 'firstLayer' in volcDict:
        newW[1] = volcDict['firstLayer'].getWord(word[1], maxLength=15, usingJson=usingJson)
    
    # OM
    if 'opinion' in volcDict:
        t = word[0]
        p = None
        if t == 'HOT': p = 2
        elif t == 'HO': p = -1
        elif t == 'OT': p = 1
        if p is not None:
            newW[p] = volcDict['opinion'].getWord(word[p], maxLength=15, usingJson=usingJson)
    
    if 'target' in volcDict:
        t = word[0]
        p = None
        if t == 'HOT': p = -1
        elif t == 'HT': p = -1
        elif t == 'T': p = 1
        elif t == 'OT': p = -1
        if p is not None:
            newW[p] = volcDict['target'].getWord(word[p], maxLength=15, usingJson=usingJson)

    if 'holder' in volcDict:
        t = word[0]
        p = None
        if t == 'HOT': p = 1
        elif t == 'HT': p = 1
        elif t == 'H': p = 1
        elif t == 'HO': p = 1
        if p is not None:
            newW[p] = volcDict['holder'].getWord(word[p], maxLength=15, usingJson=usingJson)

    return newW

def getMainVolcSize(volcDict):
    if type(volcDict) == dict:
        return len(volcDict['main'])
    elif type(volcDict) == list:
        return sum([len(v['main']) for v in volcDict])

def loadWordRankFile(filename):
    wordRank = dict()
    wordValue = dict()
    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            entry = line.strip().split(':')
            w = entry[0].strip()
            v = float(entry[1].strip())
            wordRank[w] = i
            wordValue[w] = v
    return (wordRank, wordValue)
            
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:', sys.argv[0], 'pickle outFilePrefix [wordRankFile]', file=sys.stderr)
        exit(-1)

    wordRank = None
    pickleFile = sys.argv[1]
    outFilePrefix = sys.argv[2]
    if len(sys.argv) == 4:
        wordRankFile = sys.argv[3]
        (wordRank, wordValue) = loadWordRankFile(wordRankFile)
    with open(pickleFile, 'r+b') as f:
        p = pickle.load(f)
    
    log0 = p['logList'][0]
    clf = log0['clf']
    params = p['params']
    volcDict = p['volcDict']

    with open(outFilePrefix + '_coeff.csv', 'w') as f:
        print(clf, file=f)
        print('Parameters:', toStr(params), sep=',', file=f) 
        printCoef(clf, volcDict, i2Label, sort=True, reverse=True, wordRank=wordRank, outfile=f)

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

    with open(outFilePrefix + '_log.csv', 'w') as f:
        print('C, valScore, trainScore, testScore', file=f)
        printCScore(p['logList'], 'Accuracy', y, outfile=f)
        for log in p['logList']:
            printLog(log, y, i2Label, outfile=f)
