
import sys
import math
import random
from collections import defaultdict

import numpy as np
from numpy.matrixlib.defmatrix import matrix
from scipy.sparse import csr_matrix, hstack, vstack

from sklearn import svm, cross_validation, grid_search
from sklearn.grid_search import GridSearchCV, ParameterGrid
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score, recall_score, accuracy_score, make_scorer

from sklearn.externals.joblib import Parallel, delayed
from sklearn.base import clone

# need sklearn 0.16.0
from sklearn.cross_validation import PredefinedSplit


from misc import *

'''
The whole experimental framework from X,y to results
Last Update: 2015/03/29
'''

# class for providing frameworks for running experiments
class RunExp:
    def selfTrainTest(X, y, clfList, scorerName, randSeed=1, testSize=0.2, prefix='', outfile=sys.stdout):
        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # divide data according to the topic
        #(topicList, topicX, topicy) = DataTool.divideDataByTopic(X, y, topicMap)
        
        '''
        # for each topic
        for topic in topicList:
            nowX = topicX[topic]
            nowy = topicy[topic]
            # split data
            (XTrain, XTest, yTrain, yTest) = DataTool.stratifiedSplitTrainTest(
                    nowX, nowy, randSeed, testSize)
            trainMap = [topic for i in range(0, len(yTrain))]
            testMap = [topic for i in range(0, len(yTest))]

            for clfName in clfList:
                # training using validation
                (clf, bestParam, yTrainPredict) = ML.train(XTrain, yTrain, trainMap, clfName, scorer)

                # testing 
                yTestPredict = ML.test(XTest, clf)

                # evaluation
                result = Evaluator.evaluate(yTestPredict, yTrue)
                
                # printing out results
                ResultPrinter.print("%d, " % topic, clf, bestParam, result)
        '''
        # split data
        (XTrain, XTest, yTrain, yTest) = DataTool.stratifiedSplitTrainTest(
                X, y, randSeed, testSize)

        for clfName in clfList:
            # training using validation
            (clf, bestParam, yTrainPredict) = ML.train(XTrain, yTrain, clfName, scorer)

            # testing 
            yTestPredict = ML.test(XTest, clf)

            # evaluation
            result = Evaluator.evaluate(yTestPredict, yTest)
            
            # printing out results
            ResultPrinter.print(prefix + ', selfTrainTest', clf, bestParam, scorerName, result, outfile=outfile)
    
    #FIXME
    def allTrainTest(X, y, topicMap, clfList, scorerName, randSeed=1, testSize=0.2, prefix='', outfile=sys.stdout):
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

        # training using validation
        for clfName in clfList:
            (clf, bestParam, yTrainPredict) = ML.topicTrain(XTrain, yTrain, 
                    clfName, scorerName, trainMap)

            # testing 
            scorer = Evaluator.makeScorer(scorerName, testMap)
            yTestPredict = ML.test(XTest, clf)

            # evaluation
            (topicResults, avgR) = Evaluator.topicEvaluate(yTestPredict, yTest, testMap)
                
            # printing out results
            ResultPrinter.print(prefix + ", allMixed", clf, bestParam, scorerName, avgR, outfile=outfile)

    def leaveOneTest(X, y, topicMap, clfList, scorerName, randSeed=1, prefix='', outfile=sys.stdout):
        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # divide data according to the topic
        (topicList, topicX, topicy) = DataTool.divideDataByTopic(X, y, topicMap)

        # N-1 topics are as training data, 1 topic is testing
        for topic in topicList:
            (XTrain, XTest, yTrain, yTest, trainMap, 
                    testMap) = DataTool.leaveOneTestSplit(topicX, topicy, topicList, topic)

            for clfName in clfList:
                # training using validation
                (clf, bestParam, yTrainPredict) = ML.train(XTrain, yTrain, clfName, scorer)
                # testing 
                yTestPredict = ML.test(XTest, clf)

                # evaluation
                result = Evaluator.evaluate(yTestPredict, yTest)
                
                # printing out results
                ResultPrinter.print(prefix + ", Test on %d " % topic, clf, bestParam, scorerName, result, outfile=outfile)


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
        assert testSize > 0.0 and testSize < 1.0
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
    def topicStratifiedKFold(yTrain, trainMap, n_fold=3, randSeed=1):
        assert n_fold > 1
        ySet = set(yTrain)
        (topicList, topicy) = DataTool.divideYByTopic(yTrain, trainMap)
        topicyFoldNum = dict()
        for t in topicList:
            nowy = topicy[t]
            length = len(nowy)

            # count the number of instance for each y class
            yNum = defaultdict(int)
            for i in range(0, length):
                yNum[topicy[t][i]] += 1
            
            # calculate number of instance in each fold for each class
            # topicyFoldNum[t][y]: the expected number of instances for topic t and class y
            topicyFoldNum[t] = { yClass: int(round(float(cnt)/n_fold)) for yClass, cnt in yNum.items() }
    
        # the list for making PredefinedFold
        testFold = list()
        
        # foldIndex[t][y]: current fold index for topic t and class y
        foldIndex = { t: { yClass: 0 for yClass in ySet } for t in topicList }
        # nowCnt[t][y]: the number of instance in topic t and with class y
        nowCnt = { t: { yClass: 0 for yClass in ySet } for t in topicList }
        for i, y in enumerate(yTrain):
            t = trainMap[i]
            if nowCnt[t][y] >= topicyFoldNum[t][y] and foldIndex[t][y] < n_fold - 1:
                foldIndex[t][y] += 1
                nowCnt[t][y] = 0 
            nowCnt[t][y] += 1
            testFold.append(foldIndex[t][y])
        
        # making topicMapping for testing(validation) parts of instances
        foldTopicMap = [list() for i in range(0, n_fold)]
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
        
    
# The class for providing function to do machine learning procedure
class ML:
    def train(XTrain, yTrain, clfName, scorer):
        # make cross validation iterator 
        kfold = cross_validation.StratifiedKFold(yTrain, n_folds=3)

        # get classifier and parameters to try
        (clf, parameters) = ML.__genClfAndParams(clfName)
            
        # get grid search classifier
        clfGS = GridSearchCV(clf, parameters, scoring=scorer, 
                refit=True, cv=kfold, n_jobs=-1)
        
        # refit the data by the best parameters
        clfGS.fit(XTrain, yTrain)
        # testing on training data
        yPredict = clfGS.predict(XTrain)
        
        return (clfGS.best_estimator_, clfGS.best_params_, yPredict)

    def topicTrain(XTrain, yTrain, clfName, scorerName, trainMap):
        # get classifier and parameters to try
        (clf, parameters) = ML.__genClfAndParams(clfName)

        bestParams = ML.topicGridSearchCV(clf, parameters, scorerName, XTrain, yTrain, trainMap, n_fold=3, n_jobs=-1)
        
        # refit the data by the best parameters
        clf.set_params(**bestParams)
        clf.fit(XTrain, yTrain)
                
        # testing on training data
        yPredict = clf.predict(XTrain)
        
        return (clf, bestParams, yPredict)


    def topicGridSearchCV(clf, parameters, scorerName, XTrain, yTrain, trainMap, n_fold, randSeed=1, n_jobs=1):
        # get topic stratified K-fold and its topicMapping
        (kfold, foldTopicMap) = DataTool.topicStratifiedKFold(yTrain, 
                trainMap, n_fold, randSeed=randSeed) 
        
        paramsGrid = ParameterGrid(parameters)
        
        out = Parallel(n_jobs=n_jobs)(delayed(topicGSCV_oneTask)(clone(clf), 
            params, k, train, test, XTrain, yTrain, foldTopicMap[k]) 
                for params in paramsGrid 
                for k, (train, test) in enumerate(kfold))

        bestParams = None
        bestScore = None
        n_fits = len(out)
        # collecting results
        for grid_start in range(0, n_fits, n_fold):
            avgScore = 0.0
            for r in out[grid_start:grid_start + n_fold]:
                avgScore += r['avgR'][scorerName]
            avgScore /= n_fold
            if bestScore == None or avgScore > bestScore:
                bestScore = avgScore
                bestParams = out[grid_start]['params']
        
        return bestParams
        '''
        for params in paramsGrid:
            avgScore = 0.0
            for k, (train, test) in enumerate(kfold):
                clf.set_params(**params)
                clf.fit(XTrain[train], yTrain[train])
                yPredict = clf.predict(XTrain[test])
                #print('yPredict:', len(yPredict))
                #print('yTrain[test]:', len(yTrain[test]))
                (topicResults, avgR) = Evaluator.topicEvaluate(yPredict, yTrain[test], foldTopicMap[k])
                avgScore += avgR[scorerName]
            avgScore /= n_fold
            if bestScore == None or avgScore > bestScore:
                bestScore = avgScore
                bestParams = params
        return bestParams
        '''

    def __topicGSCV_oneTask(clf, params, k, train, test, XTrain, yTrain, foldTopicMapAtK):
        clf.set_params(**params)
        clf.fit(XTrain[train], yTrain[train])
        yPredict = clf.predict(XTrain[test])
        #print('yPredict:', len(yPredict))
        #print('yTrain[test]:', len(yTrain[test]))
        (topicResults, avgR) = Evaluator.topicEvaluate(yPredict, yTrain[test], foldTopicMapAtK)
        return {'params': params, 'avgR': avgR, 'k': k }

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
                    'kernel': ('rbf', 'linear'), 
                    'C': C, 
                    'gamma': gamma
                }
            clf = svm.SVC()
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

def topicGSCV_oneTask(clf, params, k, train, test, XTrain, yTrain, foldTopicMapAtK):
    clf.set_params(**params)
    clf.fit(XTrain[train], yTrain[train])
    yPredict = clf.predict(XTrain[test])
    #print('yPredict:', len(yPredict))
    #print('yTrain[test]:', len(yTrain[test]))
    (topicResults, avgR) = Evaluator.topicEvaluate(yPredict, yTrain[test], foldTopicMapAtK)
    return {'params': params, 'avgR': avgR, 'k': k }


cmScorer = make_scorer(confusion_matrix)
macroF1Scorer = make_scorer(f1_score, average='macro')
microF1Scorer = make_scorer(f1_score, average='micro')
macroRScorer = make_scorer(recall_score, average='macro')

scorerMap = {"Accuracy" : "accuracy", "MacroF1": macroF1Scorer, 
        "MicroF1": microF1Scorer, "MacroR": macroRScorer } 

# The class for providing function to evaluate results
class Evaluator:
    def topicEvaluate(yPredict, yTrue, topicMap, topicWeights=None):
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
            r = Evaluator.evaluate(topicyTrue[t], topicyPredict[t])
            topicResults[t] = r
    
        # calculate average metric for all topics
        if topicWeights == None: # default: equal weight
            topicWeights = { t: 1.0/len(topicSet) for t in topicSet }
        avgR = Evaluator.avgTopicResults(topicResults, topicWeights)
        
        return (topicResults, avgR)

    def evaluate(yPredict, yTrue):
        # accuracy 
        accu = accuracy_score(yTrue, yPredict)
        # confusion matrix
        cm = confusion_matrix(yTrue, yPredict)
        # f1 scores
        macroF1 = f1_score(yTrue, yPredict, average='macro')
        # average recall (macro - recall
        macroR = recall_score(yTrue, yPredict, average='macro')
        return { "Accuracy": accu, "ConfusionMatrix": cm, "MacroF1": macroF1, 
                 "MacroR": macroR }

    def avgTopicResults(topicResults, weights):
        if topicResults == None or len(topicResults) == 0:
            return None
        avgAccu = 0.0
        avgMacroF1 = 0.0
        avgMacroR = 0.0
        cnt = 0
        for t, r in topicResults.items():
            avgAccu += weights[t] * r["Accuracy"]
            avgMacroF1 += weights[t] * r["MacroF1"]
            avgMacroR += weights[t] * r["MacroR"]
        
        return { "Accuracy": avgAccu, "MacroF1": avgMacroF1, "MacroR": avgMacroR }

    def makeScorer(scorerName, topicMap=None):
        if topicMap == None:
            return scorerMap[scorerName]
        else:
            return make_scorer(Evaluator.topicMacroF1Scorer, 
                    topicMap=topicMap, greater_is_bette=True)

    def topicMacroF1Scorer(yTrue, yPredict, **kwargs):
        assert 'topicMap' in set(kwargs.keys())
        topicMap = kwargs['topicMap']
        (topicResult, avgR) = Evaluator.topicEvaluate(yPredict, yTrue, topicMap)
        return avgR['MacroF1']

class ResultPrinter:
    def print(prefix, clf, params, scorerName, result, outfile):
        clfStr = "%s" % (clf)
        clfStr = clfStr[0:clfStr.find('(')]
        paramStr = "%s" % (params)
        paramStr = paramStr.replace(',', ' ').replace('\n', ' ')
        print(prefix, clfStr, paramStr, scorerName,  result['Accuracy'], 
                result['MacroF1'], result['MacroR'], sep=',', 
                file=outfile)

