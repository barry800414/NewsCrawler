
import sys
import math
import random
import tempfile
import pickle
from collections import defaultdict

import numpy as np
from numpy.matrixlib.defmatrix import matrix
from scipy.sparse import csr_matrix, hstack, vstack

from sklearn import svm, cross_validation, grid_search
from sklearn.cross_validation import StratifiedKFold 
from sklearn import preprocessing
from sklearn.grid_search import GridSearchCV, ParameterGrid
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, recall_score, accuracy_score, make_scorer
from sklearn.feature_selection import SelectKBest, SelectPercentile, RFE, chi2

from sklearn.externals.joblib import Parallel, delayed
from sklearn.base import clone

# need sklearn > 0.16.0
from sklearn.cross_validation import PredefinedSplit


from misc import *

'''
The whole experimental framework from X,y to results
Date: 2015/03/29
'''

# class for providing frameworks for running experiments
class RunExp:
    def selfTrainTest(X, y, clfList, scorerName, randSeed=1, testSize=0.2, 
            n_folds=3, fSelectConfig=None, prefix='',outfile=sys.stdout, modelDir=None):
        # check data
        if not DataTool.XyIsValid(X, y): #do nothing
            return

        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # split data
        (XTrain, XTest, yTrain, yTest) = DataTool.stratifiedSplitTrainTest(
                X, y, randSeed, testSize)
        
        # do feature selection if config is given
        if fSelectIsBeforeClf(fSelectConfig) == True:
            (XTrain, selector) = ML.fSelect(XTrain, yTrain, fSelectConfig['method'], 
                    fSelectConfig['params'])
            if XTest is not None:
                XTest = selector.transform(XTest)
            #print('Dimension:', XTest.shape, file=sys.stderr)

        returnObj = list()
        for clfName in clfList:
            # training using validation
            (clf, bestParam, bestValScore, yTrainPredict) = ML.train(XTrain, 
                    yTrain, clfName, scorer, randSeed=randSeed, n_folds=n_folds)
            
            if XTest is None or yTest is None:
                result = { 'valScore': bestValScore, scorerName: 0.0 }
            else:
                # testing 
                yTestPredict = ML.test(XTest, clf)

                # evaluation
                result = Evaluator.evaluate(yTestPredict, yTest, scorerName)
                result['valScore'] = bestValScore
            
            if modelDir is not None:
                filename = dumpModel(modelDir, clf)
            else:
                filename = None

            # printing out results
            ResultPrinter.print(prefix + ', selfTrainTest', "%d %d" % (X.shape[0], 
                XTrain.shape[1]), clfName, bestParam, scorerName, randSeed, 
                    result, filename, outfile=outfile)

            returnObj.append( { 'clfName': clfName, 'clf': clf, 'param': bestParam, 
                'result': result, 'data':{'XTrain': XTrain, 'yTrain': yTrain, 
                    'XTest': XTest, 'yTest': yTest } } )
        
        return returnObj

    def selfTrainTestNFold(X, y, clfList, scorerName, randSeed=1, test_folds=10, 
            n_folds=3, fSelectConfig=None, prefix='',outfile=sys.stdout, modelDir=None):
        # check data
        if not DataTool.XyIsValid(X, y): #do nothing
            return

        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # split data in N-fold
        skf = StratifiedKFold(y, n_folds=test_folds, shuffle=True, random_state=randSeed)
        for clfName in clfList:
            returnObj = list()
            resultList = list()
            for train_index, test_index in skf:
                XTrain, XTest = X[train_index], X[test_index]
                yTrain, yTest = y[train_index], y[test_index]
        
                # do feature selection if config is given
                if fSelectIsBeforeClf(fSelectConfig) == True:
                    print('before selection:', XTrain.shape, file=sys.stderr)
                    (XTrain, selector) = ML.fSelect(XTrain, yTrain, fSelectConfig['method'], 
                            fSelectConfig['params'])
                    print('after selection:', XTrain.shape, file=sys.stderr)
                    if XTest is not None:
                        XTest = selector.transform(XTest)

                # training using validation
                (clf, bestParam, bestValScore, yTrainPredict) = ML.train(XTrain, 
                        yTrain, clfName, scorer, randSeed=randSeed, n_folds=n_folds)
                
                if XTest is None or yTest is None:
                    resultList.append({ 'valScore': bestValScore, scorerName: 0.0 })
                else:
                    # testing 
                    yTestPredict = ML.test(XTest, clf)

                    # evaluation
                    result = Evaluator.evaluate(yTestPredict, yTest, scorerName)
                    result['valScore'] = bestValScore
                    resultList.append(result)
                
                if modelDir is not None:
                    filename = dumpModel(modelDir, clf)
                else:
                    filename = None
            
            # average NFold results
            result = Evaluator.avgNFoldResult(resultList)

            # printing out results
            ResultPrinter.print(prefix + ', selfTrainTest', "%d %d" % (X.shape[0], 
                XTrain.shape[1]), clfName, bestParam, scorerName, randSeed, 
                    result, filename, outfile=outfile)

            returnObj.append( { 'clfName': clfName, 'clf': clf, 'param': bestParam, 
                'result': result, 'data':{'XTrain': XTrain, 'yTrain': yTrain, 
                    'XTest': XTest, 'yTest': yTest } } )
        
        return returnObj


    def allTrainTest(X, y, topicMap, clfList, scorerName, randSeed=1, testSize=0.2, 
            n_folds=3, fSelectConfig=None, prefix='', outfile=sys.stdout, modelDir=None):
        # check data
        if not DataTool.XyIsValid(X, y): #do nothing
            return

        # divide data according to the topic
        (topicList, topicX, topicy) = DataTool.divideDataByTopic(X, y, topicMap)

        # split data for each topic, merge data into one training data and testing data
        topicXTrain = dict()
        topicXTest = dict()
        topicyTrain = dict()
        topicyTest = dict()
        for topic in topicList:
            nowX = topicX[topic]
            nowy = topicy[topic]
            # split data
            (XTrain, XTest, yTrain, yTest) = DataTool.stratifiedSplitTrainTest(
                    nowX, nowy, randSeed, testSize)
            topicXTrain[topic] = XTrain
            topicXTest[topic] = XTest
            topicyTrain[topic] = yTrain
            topicyTest[topic] = yTest
        (XTrain, XTest, yTrain, yTest, trainMap, testMap) = DataTool.mergeData(
                topicXTrain, topicXTest, topicyTrain, topicyTest, topicList)

        # do feature selection if config is given
        if fSelectIsBeforeClf(fSelectConfig) == True:
            (XTrain, selector) = ML.fSelect(XTrain, yTrain, fSelectConfig['method'], 
                    fSelectConfig['params'])
            if XTest is not None:
                XTest = selector.transform(XTest)
            #print('Dimension:', XTest.shape, file=sys.stderr)

        returnObj = list()
        # training using validation
        for clfName in clfList:
            #print('In Cross Validation... ', end='', file=sys.stderr)
            (clf, bestParam, bestValScore, yTrainPredict) = ML.topicTrain(XTrain, 
                    yTrain, clfName, scorerName, trainMap, randSeed=randSeed, n_folds=3)
            #print('Done', file=sys.stderr)

            if XTest is None or yTest is None:
                result = { 'valScore': bestValScore, scorerName: 0.0 }
            else:
                # testing 
                scorer = Evaluator.makeScorer(scorerName, testMap)

                #print('In testing... ', end='', file=sys.stderr)
                yTestPredict = ML.test(XTest, clf)

                # evaluation
                (topicResults, avgR) = Evaluator.topicEvaluate(yTestPredict, yTest, testMap, scorerName=scorerName)
                avgR['valScore'] = bestValScore
                #print('Done', file=sys.stderr)

            if modelDir is not None:
                filename = dumpModel(modelDir, clf)
            else:
                filename = None

            # printing out results
            ResultPrinter.print(prefix + ", allMixed", "%d %d" % (X.shape[0], 
                XTrain.shape[1]), clfName, bestParam, scorerName, randSeed, 
                avgR, filename, outfile=outfile)
            
            returnObj.append( { 'clfName': clfName, 'clf': clf, 'param': bestParam, 
                'result': avgR, 'data':{'XTrain': XTrain, 'yTrain': yTrain, 
                    'XTest': XTest, 'yTest': yTest } } )

        return returnObj

    def leaveOneTest(X, y, topicMap, clfList, scorerName, testTopic=None, randSeed=1, 
            n_folds=3, fSelectConfig=None, prefix='', outfile=sys.stdout, modelDir=None):
        # check data
        if not DataTool.XyIsValid(X, y): #do nothing
            return

        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # divide data according to the topic
        (topicList, topicX, topicy) = DataTool.divideDataByTopic(X, y, topicMap)

        # N-1 topics are as training data, 1 topic is testing
        # if the test topic id is given, then only test it
        if testTopic is None:
            testTopic = list(topicList)
       

        returnObj = dict()
        for topic in testTopic:
            returnObj[topic] = list()
            (XTrain, XTest, yTrain, yTest, trainMap, 
                    testMap) = DataTool.leaveOneTestSplit(topicX, topicy, topicList, topic)

            # do feature selection if config is given
            if fSelectIsBeforeClf(fSelectConfig) == True:
                (XTrain, selector) = ML.fSelect(XTrain, yTrain, fSelectConfig['method'], 
                        fSelectConfig['params'])
                if XTest is not None:
                    XTest = selector.transform(XTest)
                #print('Dimension:', XTest.shape, file=sys.stderr)
            for clfName in clfList:
                # training using validation
                #print('In Cross Validation... ', end='', file=sys.stderr)
                (clf, bestParam, bestValScore, yTrainPredict) = ML.train(XTrain, 
                        yTrain, clfName, scorer, randSeed=randSeed, n_folds=n_folds)
                #print('Done', file=sys.stderr)
                
                if XTest is None or yTest is None:
                    result = { 'valScore': bestValScore, scorerName: 0.0 }
                else:
                    # testing 
                    #print('In testing... ', end='', file=sys.stderr)
                    yTestPredict = ML.test(XTest, clf)

                    # evaluation
                    result = Evaluator.evaluate(yTestPredict, yTest, scorerName)
                    result['valScore'] = bestValScore
                    #print('Done', file=sys.stderr)

                if modelDir is not None:
                    filename = dumpModel(modelDir, clf)
                else:
                    filename = None

                # printing out results
                ResultPrinter.print(prefix + ", Test on %d " % topic, "%d %d" % (
                    X.shape[0], XTrain.shape[1]), clfName, bestParam, scorerName,
                    randSeed, result, filename, outfile=outfile)
                returnObj[topic].append( { 'clfName': clfName, 'clf': clf, 
                    'param': bestParam, 'result': result, 'data':{'XTrain': XTrain, 
                        'yTrain': yTrain, 'XTest': XTest, 'yTest': yTest }  } )
        return returnObj
    
    # higher layer function for running task
    # taskType: SelfTrainTest, AllTrainTest, LeaveOneTest
    def runTask(X, y, volcDict, taskType, params, clfList, randSeedList, testSize, n_folds, 
        targetScore, fSelectConfig, topicMap=None, topicId=None):
        print('X: (%d, %d)' % (X.shape[0], X.shape[1]), file=sys.stderr)
        rsList = list()
        for randSeed in randSeedList:
            if taskType == 'SelfTrainTest':
                prefix = "%s, %s, %s" % (topicId, toStr(params), toStr(["content"]))
                # FIXME: only support self train test now
                if testSize <= 1.0:
                    rs = RunExp.selfTrainTest(X, y, clfList, targetScore, 
                            randSeed=randSeed, testSize=testSize, n_folds=n_folds, 
                            fSelectConfig=fSelectConfig, prefix=prefix)
                else:
                    rs = RunExp.selfTrainTestNFold(X, y, clfList, targetScore, 
                        randSeed=randSeed, test_folds=testSize, n_folds=n_folds, 
                        fSelectConfig=fSelectConfig, prefix=prefix)

                if rs is None:
                    return None
                for r in rs:
                    r['volcDict'] = volcDict
                    r['X'] = X
                    r['y'] = y
                    r['params'] = params

            elif taskType == 'AllTrainTest': 
                prefix = "%s, %s, %s" % ('all', toStr(params), toStr(["content"]))
                rs = RunExp.allTrainTest(X, y, topicMap, clfList, targetScore, 
                        randSeed=randSeed, testSize=testSize, n_folds=n_folds, 
                        fSelectConfig=fSelectConfig, prefix=prefix)
                if rs is None:
                    return None
                for r in rs:
                    r['volcDict'] = volcDict
                    r['X'] = X
                    r['y'] = y
                    r['params'] = params

            elif taskType == 'LeaveOneTest':
                prefix = "%s, %s, %s" % (topicId, toStr(params), toStr(["content"]))
                rs = RunExp.leaveOneTest(X, y, topicMap, clfList, targetScore, 
                        randSeed=randSeed, testTopic=[topicId], n_folds=n_folds,
                        fSelectConfig=fSelectConfig, prefix=prefix)
                if rs is None:
                    return None
                for r in rs[topicId]:
                    r['volc'] = volcDict
                    r['X'] = X
                    r['y'] = y
                    r['params'] = params
            rsList.append(rs)

        return rsList


def dumpModel(dir, clf):
    tmpF = tempfile.NamedTemporaryFile(mode='w+b', dir=dir, prefix='clf', delete=False)
    with tmpF.file as f:
        pickle.dump(clf, f)
    return tmpF.name
        

# The class for providing functions to manipulate data
class DataTool:
    def divideDataByTopic(X, y, topicMap):
        assert X.shape[0] == len(y) and len(y) == len(topicMap)
        topics = set()
        index = dict()
        for i, t in enumerate(topicMap):
            if t not in topics:
                topics.add(t)
                index[t] = list()
            index[t].append(i)
        
        topicX = dict()
        topicy = dict()
        for t in topics:
            topicX[t] = X[index[t]]
            topicy[t] = y[index[t]]
        
        return (list(topics), topicX, topicy)

    def divideYByTopic(y, topicMap):
        assert len(y) == len(topicMap)
        topics = set()
        index = dict()
        for i, t in enumerate(topicMap):
            if t not in topics:
                topics.add(t)
                index[t] = list()
            index[t].append(i)

        topicy = dict()
        for t in topics:
            topicy[t] = y[index[t]]
        return (list(topics), topicy)

    # In order to prevent 0 cases in training or testing data (s.t. evaluation 
    # metric is illed-defined), we first get the expected number of instance first
    def stratifiedSplitTrainTest(X, y, randSeed=1, testSize=0.2):
        assert X.shape[0] == len(y)
        assert testSize >= 0.0 and testSize < 1.0
        #print('testSize:', testSize)
        
        if testSize == 0.0:
            return (X, None, y, None)
        length = len(y)

        # count the number of instance for each y class
        yNum = defaultdict(int)
        for i in range(0, length):
            yNum[y[i]] += 1

        # calculate expected number of instance for each class
        yTestNum = { yi: int(math.ceil(cnt*testSize)) for yi, cnt in yNum.items() }
        yTrainNum = { yi: yNum[yi] - yTestNum[yi] for yi in yNum.keys() }
        
        # random shuffle
        index = [i for i in range(0, length)]
        random.seed(randSeed)
        random.shuffle(index)

        nowNum = { yi: 0 for yi in yNum.keys() }
        trainIndex = list()
        testIndex = list()
        for i in index:
            if nowNum[y[i]] < yTrainNum[y[i]]:
                trainIndex.append(i)
                nowNum[y[i]] += 1
            else:
                testIndex.append(i)
        XTrain = X[trainIndex]
        XTest = X[testIndex]
        yTrain = y[trainIndex]
        yTest = y[testIndex]
        
        #print('y:', y)
        #print('yTrain:', yTrain)
        #print('yTest:', yTest)
        
        return (XTrain, XTest, yTrain, yTest)

    # merge topicX and topicy 
    def mergeData(topicXTrain, topicXTest, topicyTrain, topicyTest, topicList):
        assert len(topicList) != 0
        XTrainList = list()
        XTestList = list()
        yTrainList = list()
        yTestList = list()
        trainMap = list()
        testMap = list()
        for t in topicList:
            assert topicXTrain[t].shape[0] == len(topicyTrain[t])
            assert topicXTest[t].shape[0] == len(topicyTest[t])
            XTrainList.append(topicXTrain[t])
            XTestList.append(topicXTest[t])
            yTrainList.append(topicyTrain[t])
            yTestList.append(topicyTest[t])
            trainMap.extend([t for i in range(0, len(topicyTrain[t]))])
            testMap.extend([t for i in range(0, len(topicyTest[t]))])
        
        xType = type(next (iter (topicXTrain.values())))
        if xType == matrix: #dense
            XTrain = np.concatenate(XTrainList, axis=0)
            XTest = np.concatenate(XTestList, axis=0)
        elif xType == csr_matrix: #sparse
            XTrain = vstack(XTrainList)
            XTest = vstack(XTestList)

        yTrain = np.concatenate(yTrainList, axis=0)
        yTest = np.concatenate(yTestList, axis=0)

        return (XTrain, XTest, yTrain, yTest, trainMap, testMap) 

    def leaveOneTestSplit(topicX, topicy, topicList, testTopic):
        XTrainList = list()
        yTrainList = list()
        trainMap = list()
        for t in topicList:
            if t == testTopic:
                XTest = topicX[t]
                yTest = topicy[t]
            else:
                XTrainList.append(topicX[t])
                yTrainList.append(topicy[t])
                trainMap.extend([t for i in range(0, len(topicy[t]))])
        
        # concatenate XTrain Matrix
        xType = type(XTrainList[0])
        if xType == matrix: #dense
            XTrain = np.concatenate(XTrainList, axis=0)
        elif xType == csr_matrix: #sparse
            XTrain = vstack(XTrainList)
        # concatenate yTrain vector
        yTrain = np.concatenate(yTrainList, axis=0)

        testMap = [testTopic for i in range(0, len(yTest))]
        return (XTrain, XTest, yTrain, yTest, trainMap, testMap)

    # for each topic, do stratified K fold, and then merge them
    def topicStratifiedKFold(yTrain, trainMap, n_folds, randSeed=1):
        assert n_folds > 1
        #print('n_folds:', n_folds, end='', file=sys.stderr) 
        ySet = set(yTrain)
        
        # divide data by topic
        (topicList, topicy) = DataTool.divideYByTopic(yTrain, trainMap)
        topicyFoldNum = dict()
        
        # for each topic, do stratified K fold 
        for t in topicList:
            nowy = topicy[t]
            length = len(nowy)

            # count the number of instance for each y class
            yNum = defaultdict(int)
            for i in range(0, length):
                yNum[topicy[t][i]] += 1
            
            # calculate the expected number of instance in each fold for each class
            # topicyFoldNum[t][y]: the expected number of instances for topic t and class y
            topicyFoldNum[t] = { yClass: int(round(float(cnt)/n_folds)) for yClass, cnt in yNum.items() }
    
        # the list for making PredefinedFold
        testFold = [0 for i in range(0, len(yTrain))]
        
        # foldIndex[t][y]: current fold index for topic t and class y
        foldIndex = { t: { yClass: 0 for yClass in ySet } for t in topicList }
        # nowCnt[t][y]: the number of instance in topic t and with class y
        nowCnt = { t: { yClass: 0 for yClass in ySet } for t in topicList }
        
        # random shuffle
        index = [i for i in range(0, len(yTrain))]
        random.seed(randSeed)
        random.shuffle(index)
        
        #for i, y in enumerate(yTrain):
        for i in index:
            y = yTrain[i]
            t = trainMap[i]
            if nowCnt[t][y] >= topicyFoldNum[t][y] and foldIndex[t][y] < n_folds - 1:
                foldIndex[t][y] += 1
                nowCnt[t][y] = 0 
            nowCnt[t][y] += 1
            testFold[i] = foldIndex[t][y]
        
        # making topicMapping for testing(validation) parts of instances
        foldTopicMap = [list() for i in range(0, n_folds)]
        for i, fi in enumerate(testFold):
            foldTopicMap[fi].append(trainMap[i])

        #print('yTrain:', yTrain)
        #print('trainMap:', trainMap)
        #print('testFold:', testFold)
        #print('foldTopicMap', foldTopicMap)
        return (PredefinedSplit(testFold), foldTopicMap)

    # horzontally merge two matrix, height should be identical
    def hstack(X1, X2):
        if X1.shape[0] != X2.shape[0]:
            print('X1%s and X2%s has different height' % (X1.shape, X2.shape), file=sys.stderr)
            return None
        if type(X1) != type(X2):
            print('X1(%s) and X2(%s) are different type of matrix' % (type(X1), type(X2)), file=sys.stderr)
            return None

        # concatenate XTrain Matrix
        xType = type(X1)
        if xType == matrix: #dense
            return np.concatenate((X1, X2), axis=1)
        elif xType == csr_matrix: #sparse
            return csr_matrix(hstack((X1, X2)))
        
    def XyIsValid(X, y):
        if X.shape[0] != len(y):
            print('X.shape[0] != len(y)', file=sys.stderr)
            return False
        elif X.shape[0] == 0:
            print('X.shape[0] == 0', file=sys.stderr)
            return False
        elif X.shape[1] == 0:
            print('X.shape[1] == 0', file=sys.stderr)
            return False
        else:
            return True
    
    def saveAsLibSVMFormat(X, y, outfile=sys.stdout):
        assert X.shape[0] == len(y)
        if type(X) == csr_matrix:
            (rowNum, colNum) = X.shape
            colIndex = X.indices
            rowPtr = X.indptr
            data = X.data
            nowPos = 0
    
            sumOfCol = [0.0 for i in range(0, colNum)]
            for ri in range(0, rowNum):
                print(y[ri], end='', file=outfile)
                for ci in colIndex[rowPtr[ri]:rowPtr[ri+1]]:
                    value = data[nowPos]
                    print(' %d:%f' % (ci, value), end='', file=outfile)
                    nowPos += 1
                print('', file=outfile)
    
    # preprocessing the feature matrix (including standardization, 
    # minMax scaling, normalization and binarization)
    def preprocessX(X, method, params):
        success = False
        # standardization: transforming each column(feature) to zero-mean, std=1
        if method in ['std', 'standardization']:
            print('Using standardization ...', file=sys.stderr)
            scaler = preprocessing.StandardScaler(with_mean=params['with_mean'], 
                    with_std=params['with_std']).fit(X)
            preX = scaler.transform(X)
            success = True
        # minMax scaling: transforming each column(feature) to [a, b]
        # (usually [-1, 1] or [0, 1])
        elif method in ['minmax', 'minMax']:
            if 'feature_range' in params:
                print('Using MinMax scaling to', params['feature_range'], file=sys.stderr)
                scaler = preprocessing.MinMaxScaler(params['feature_range'])
                preX = scaler.fit_transform(X)
                success = True
        # normalization: transforming scaling each row(an instance) to fixed length 
        # (usually L1-norm or L2-norm to length 1)
        elif method in ['norm', 'normalization']:
            if 'norm' in params:
                print('Using normalization (%s)' % (params['norm']), file=sys.stderr)
                preX = preprocessing.normalize(X, norm=params['norm'])
                success = True
        # binarization: transforming each entry to 0 or 1 by given threshold
        elif method in ['0/1', 'binary', 'binarization']:
            if 'threshold' in params:
                binarizer = preprocessing.Binarizer(threshold=params['threshold'])
                preX = binarizer.transform(X)
                success = True
        else:
            print('Preprocessing method not found', file=sys.stderr)
        
        if not success:
            print('preprocessing X failed', file=sys.stderr)
            assert 1 == 0

        return preX

# The class for providing function to do machine learning procedure
class ML:
    def train(XTrain, yTrain, clfName, scorer, n_folds, randSeed=1, fSelectConfig=None):
        # make cross validation iterator 
        #print(' n_folds:', n_folds, end='', file=sys.stderr) 
        kfold = cross_validation.StratifiedKFold(yTrain, n_folds=n_folds, 
                shuffle=True, random_state=randSeed)

        # get classifier and parameters to try
        (clf, parameters) = ML.__genClfAndParams(clfName)

        # get grid search classifier
        #print('->grid search ', end='', file=sys.stderr)
        clfGS = GridSearchCV(clf, parameters, scoring=scorer, 
                refit=True, cv=kfold, n_jobs=-1)
        
        # refit the data by the best parameters
        #print('->refit ', end='', file=sys.stderr)
        clfGS.fit(XTrain, yTrain)

        # get validation score
        bestValScore = clfGS.best_score_

        # testing on training data
        yPredict = clfGS.predict(XTrain)

        return (clfGS.best_estimator_, clfGS.best_params_, bestValScore, yPredict)

    def topicTrain(XTrain, yTrain, clfName, scorerName, trainMap, n_folds, randSeed=1):
        # get classifier and parameters to try
        (clf, parameters) = ML.__genClfAndParams(clfName)
        
        #print('n_folds:%d -> topic grid search ' %(n_folds), end='', file=sys.stderr)
        (bestValScore, bestParams) = ML.topicGridSearchCV(clf, parameters, 
                scorerName, XTrain, yTrain, trainMap, n_folds=n_folds, 
                randSeed=randSeed, n_jobs=-1)
        
        # refit the data by the best parameters
        clf.set_params(**bestParams)
        #print('-> topic refit ', end='', file=sys.stderr)
        clf.fit(XTrain, yTrain)
        
        # testing on training data
        yPredict = clf.predict(XTrain)
        
        return (clf, bestParams, bestValScore, yPredict)


    def topicGridSearchCV(clf, parameters, scorerName, XTrain, yTrain, 
            trainMap, n_folds, randSeed=1, n_jobs=1):
        # get topic stratified K-fold and its topicMapping
        (kfold, foldTopicMap) = DataTool.topicStratifiedKFold(yTrain, 
                trainMap, n_folds, randSeed=randSeed) 
        
        paramsGrid = ParameterGrid(parameters)
        
        out = Parallel(n_jobs=n_jobs)(delayed(topicGSCV_oneTask)(clone(clf), 
            params, scorerName, k, train, test, XTrain, yTrain, foldTopicMap[k]) 
                for params in paramsGrid 
                for k, (train, test) in enumerate(kfold))

        bestParams = None
        bestScore = None
        n_fits = len(out)
        # collecting results
        for grid_start in range(0, n_fits, n_folds):
            avgScore = 0.0
            for r in out[grid_start:grid_start + n_folds]:
                avgScore += r['avgR'][scorerName]
            avgScore /= n_folds
            if bestScore is None or avgScore > bestScore:
                bestScore = avgScore
                bestParams = out[grid_start]['params']
        
        return (bestScore, bestParams)

    def test(XTest, bestClf):
        yPredict = bestClf.predict(XTest)
        return yPredict

    def __genClfAndParams(clfName):
        if clfName == 'NaiveBayes':
            parameters = {
                'alpha': [0.5, 1.0, 2.0],
                'fit_prior': [True, False]
            }
            clf = MultinomialNB()
        elif clfName == 'MaxEnt' or clfName == 'LogReg':
            parameters = {
                'penalty': ('l1', 'l2'),
                'C': [0.5, 1, 2],
            }
            clf = LogisticRegression()
        elif clfName == 'SVM':
            C = [math.pow(2, i) for i in range(-1,11,2)]
            gamma = [math.pow(2, i) for i in range(-11,-1,2)]
            parameters = {
                    'kernel': ('rbf', ), 
                    'C': C, 
                    'gamma': gamma
                }
            clf = svm.SVC()
        elif clfName == 'LinearSVM' or clfName == 'LinearSVC':
            C = [math.pow(2, i) for i in range(-3,13,2)]
            parameters = {
                    'C': C        
                }
            clf = svm.LinearSVC()
        elif clfName == 'RandomForest': #depricated: RF does not support sparse matrix
            estNum = [5, 10, 15, 20]
            minSampleSplit = [1, 2]
            parameters = {
                    "n_estimators": estNum,
                    "min_samples_split": minSampleSplit
                }
            clf = RandomForestClassifier()
        else:
            print('Classifier name cannot be identitified', file=sys.stderr)
            return None

        return (clf, parameters) 

    # feature selection 
    # FIXME: for the method using classifier, the target score is Accuracy (rather than MacroF1)
    def fSelect(XTrain, yTrain, method, params, clf=None, scorer=None):
        if method in ["chi", "chi-square"]:
            if 'top_k' in params:
                print('Selecting features with top %d chi-square value ...' % params['top_k'], file=sys.stderr) 
                selector = SelectKBest(chi2, k=params['top_k']).fit(XTrain, yTrain)
                newX = selector.transform(XTrain)
            elif 'percentage' in params:
                print('Selecting %d%% features with top chi-square value ...' % params['percentage'], file=sys.stderr)
                selector = SelectPercentile(chi2, percentile=params['percentage']).fit(XTrain, yTrain)
                newX = selector.transform(XTrain)
        elif method in ["rfe", "RFE", 'RecursiveFeatureElimination']:
            if 'n_features_to_select' in params and 'step' in params:
                print('Selecting features using RecursiveFeatureElimination (with original classifier) ...', file=sys.stderr)
                selector = RFE(clf, params['n_features_to_select'], step=params['step']).fit(XTrain, yTrain)
                newX = selector.transform(XTrain)
        elif method in ['LinearSVM', 'LinearSVC']:
            if 'C' in params:
                print('Selecting features using Linear SVM (L1 regularizaton) ...', file=sys.stderr)
                selector = svm.LinearSVC(C=params['C'], penalty="l1", dual=False).fit(XTrain, yTrain)
                newX = selector.transform(XTrain)
        elif method in ['rf', 'RF', 'RandomForest']:
            print('Selecting features using RandomForest ...', file=sys.stderr)
            selector = RandomForestClassifier().fit(XTrain, yTrain)
            newX = selector.transform(XTrain)
        return (newX, selector)

    # using cross-validation to do feature selection
    def fSelectCV(XTrain, yTrain, clfName, params):
        pass
        #return (clfGS.best_estimator_, clfGS.best_params_, )

def fSelectIsBeforeClf(fSelectConfig):
    if fSelectConfig == None or 'method' not in fSelectConfig:
        return None
    method = fSelectConfig['method']
    if method in ["chi", "chi-square", 'LinearSVM', 'LinearSVC', 'rf', 'RF', 'RandomForest']:
        return True
    elif method in ["rfe", "RFE", 'RecursiveFeatureElimination']:
        return False
    else:
        return None

def topicGSCV_oneTask(clf, params, scorerName, k, train, test, XTrain, yTrain, foldTopicMapAtK):
    clf.set_params(**params)
    clf.fit(XTrain[train], yTrain[train])
    yPredict = clf.predict(XTrain[test])
    #print('yPredict:', len(yPredict))
    #print('yTrain[test]:', len(yTrain[test]))
    (topicResults, avgR) = Evaluator.topicEvaluate(yPredict, yTrain[test], foldTopicMapAtK, scorerName=scorerName)
    return {'params': params, 'avgR': avgR, 'k': k }


macroF1Scorer = make_scorer(f1_score, average='macro')
macroRScorer = make_scorer(recall_score, average='macro')
scorerMap = {"Accuracy" : "accuracy", "MacroF1": macroF1Scorer, 
        "F1": "f1", "MacroR": macroRScorer } 

# The class for providing function to evaluate results
class Evaluator:
    def topicEvaluate(yPredict, yTrue, topicMap, topicWeights=None, scorerName='MacroF1'):
        assert len(yTrue) == len(yPredict) and len(yTrue) == len(topicMap)
        length = len(yTrue)

        # find all possible topic
        topicSet = set(topicMap)

        # divide yTrue and yPredict
        topicyTrue = {t:list() for t in topicSet}
        topicyPredict = {t:list() for t in topicSet}
    
        for i, t in enumerate(topicMap):
            topicyTrue[t].append(yTrue[i])
            topicyPredict[t].append(yPredict[i])
    
        for t in topicSet:
            topicyTrue[t] = np.array(topicyTrue[t])
            topicyPredict[t] = np.array(topicyPredict[t])

        # evaluation for each topic
        topicResults = dict()
        for t in topicSet:
            assert len(topicyTrue[t]) == len(topicyPredict[t]) and len(topicyTrue[t]) != 0
            r = Evaluator.evaluate(topicyTrue[t], topicyPredict[t], scorerName)
            topicResults[t] = r
    
        # calculate average metric for all topics
        if topicWeights is None: # default: equal weight
            topicWeights = { t: 1.0/len(topicSet) for t in topicSet }
        avgR = Evaluator.avgTopicResults(topicResults, topicWeights)
        
        return (topicResults, avgR)

    def evaluate(yPredict, yTrue, scorerName='MacroF1'):
        if scorerName == 'Accuracy':
            # accuracy 
            #print('In accu ...', file=sys.stderr)
            score = accuracy_score(yTrue, yPredict)
        elif scorerName == 'F1':
            # f1 scores
            #print('In F1 ...', file=sys.stderr)
            score = f1_score(yTrue, yPredict, average='binary')
        elif scorerName == 'MacroF1':
            #print('In MacroF1 score ...', file=sys.stderr) 
            score = f1_score(yTrue, yPredict, average='macro')
        elif scorerName == "MacroR":
            # average recall (macro recall)
            #print('In Macro recall ...', file=sys.stderr)
            score = recall_score(yTrue, yPredict, average='macro')
        return { scorerName: score }
    
    def avgNFoldResult(resultList):
        avgScore = defaultdict(float)
        for result in resultList:
            for key, value in result.items():
                avgScore[key] += value
        for key in avgScore.keys():
            avgScore[key] = avgScore[key] / len(resultList)
        return avgScore

    def avgTopicResults(topicResults, weights):
        if topicResults is None or len(topicResults) == 0:
            return None
        cnt = 0
        avgScore = defaultdict(float)
        for t, r in topicResults.items():
            for scorerName in r.keys():
                avgScore[scorerName] += weights[t] * r[scorerName]
        
        return dict(avgScore)

    def makeScorer(scorerName, topicMap=None):
        if topicMap is None:
            return scorerMap[scorerName]
        else:
            return make_scorer(Evaluator.topicMacroF1Scorer, 
                    topicMap=topicMap, greater_is_bette=True)

    def topicMacroF1Scorer(yTrue, yPredict, **kwargs):
        assert 'topicMap' in set(kwargs.keys())
        topicMap = kwargs['topicMap']
        (topicResult, avgR) = Evaluator.topicEvaluate(yPredict, yTrue, topicMap, scorerName=scorerName)
        return avgR['MacroF1']

class ResultPrinter:
    def printFirstLine(outfile=sys.stdout):
        print('topicId, model settings, column source,'
          ' experimental settings, classifier, scorer, dimension,'
          ' parameters, randSeed, valScore, testScore,'
          ' modelPath(pickle)', file=outfile)

    def getDataType():
        return ('str', 'str', 'str', 'str', 'str', 'str', 'str', 
                'str', 'int', 'float', 'float', 'str')
    
    def print(prefix, Xshape, clfName, params, scorerName, randSeed, 
            result, filename, outfile):
        paramStr = toStr("%s" % params)
        print(prefix, clfName, scorerName, Xshape, paramStr, randSeed, 
                result['valScore'], result[scorerName], filename, sep=',', 
                file=outfile)

# nowBestR: now best result
def keepBestResult(nowBestR, nextRSList, scorerName, largerIsBetter=True, topicId=None):
    if nextRSList is None:
        return nowBestR
    
    if nowBestR is None:
        nowScore = -1.0
    else:
        nowScore = nowBestR['result'][scorerName]
    for rs1 in nextRSList: 
        if rs1 is None:
            continue
        if topicId is not None:
            rs = rs1[topicId]
        else:
            rs = rs1
        for r in rs:
            nextScore = r['result'][scorerName]
            if largerIsBetter:
                if nextScore > nowScore:
                    nowScore = nextScore
                    nowBestR = r
            else:
                if nextScore < nowScore:
                    nowScore = nextScore
                    nowBestR = r
    return nowBestR
