
import sys
import math
import random
from collections import defaultdict

import numpy as np

from sklearn import svm, cross_validation, grid_search
from sklearn.grid_search import GridSearchCV, ParameterGrid
from sklearn.metrics import confusion_matrix, f1_score, recall_score, accuracy_score, make_scorer

# need sklearn 0.16.0
from sklearn.cross_validation import PredefinedSplit

from misc import *

'''
The whole experimental framework from X,y to results
Date: 2015/03/29
'''

def genRandY(y):
    ySet = set(y)
    yLength = len(y)
    randY = np.array([random.randint(0, len(ySet) - 1) for j in range(0, yLength)])
    return randY


# class for providing frameworks for running experiments
class RunExp:
    def selfTrainTest(y, scorerName, randSeed=1, testSize=0.2):
        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # split data
        (yTrain, yTest) = DataTool.stratifiedSplitTrainTest(y, randSeed, testSize)
        
        # testing 
        yTestPredict = genRandY(yTest)

        # evaluation
        r = Evaluator.evaluate(yTestPredict, yTest)
        return r

    def allTrainTest(y, topicMap, scorerName, randSeed=1, testSize=0.2):
        # divide data according to the topic
        (topicList, topicy) = DataTool.divideDataByTopic(y, topicMap)

        # split data for each topic, merge data into one training data and testing data
        topicyTrain = dict()
        topicyTest = dict()
        for topic in topicList:
            nowy = topicy[topic]
            # split data
            (yTrain, yTest) = DataTool.stratifiedSplitTrainTest(nowy, randSeed, testSize)
            topicyTrain[topic] = yTrain
            topicyTest[topic] = yTest
        (yTrain, yTest, trainMap, testMap) = DataTool.mergeData(topicyTrain, topicyTest, topicList)

        # testing 
        scorer = Evaluator.makeScorer(scorerName, testMap)
        yTestPredict = genRandY(yTest)

        # evaluation
        (topicResults, avgR) = Evaluator.topicEvaluate(yTestPredict, yTest, testMap)
        return avgR

    def leaveOneTest(y, topicMap, scorerName, testTopic=None, randSeed=1):
        # making scorer
        scorer = Evaluator.makeScorer(scorerName)

        # divide data according to the topic
        (topicList, topicy) = DataTool.divideDataByTopic(y, topicMap)

        (yTrain, yTest, trainMap, testMap) = DataTool.leaveOneTestSplit(topicy, topicList, testTopic)

        # testing 
        yTestPredict = genRandY(yTest)

        # evaluation
        r = Evaluator.evaluate(yTestPredict, yTest)

        return r
    
# The class for providing functions to manipulate data
class DataTool:
    def divideDataByTopic(y, topicMap):
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
    def stratifiedSplitTrainTest(y, randSeed=1, testSize=0.2):
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
        yTrain = y[trainIndex]
        yTest = y[testIndex]
        
        #print('y:', y)
        #print('yTrain:', yTrain)
        #print('yTest:', yTest)
        
        return (yTrain, yTest)

    # merge topicX and topicy 
    def mergeData(topicyTrain, topicyTest, topicList):
        assert len(topicList) != 0
        yTrainList = list()
        yTestList = list()
        trainMap = list()
        testMap = list()
        for t in topicList:
            yTrainList.append(topicyTrain[t])
            yTestList.append(topicyTest[t])
            trainMap.extend([t for i in range(0, len(topicyTrain[t]))])
            testMap.extend([t for i in range(0, len(topicyTest[t]))])
        
        yTrain = np.concatenate(yTrainList, axis=0)
        yTest = np.concatenate(yTestList, axis=0)

        return (yTrain, yTest, trainMap, testMap) 

    def leaveOneTestSplit(topicy, topicList, testTopic):
        yTrainList = list()
        trainMap = list()
        for t in topicList:
            if t == testTopic:
                yTest = topicy[t]
            else:
                yTrainList.append(topicy[t])
                trainMap.extend([t for i in range(0, len(topicy[t]))])
        
        # concatenate yTrain vector
        yTrain = np.concatenate(yTrainList, axis=0)

        testMap = [testTopic for i in range(0, len(yTest))]
        return (yTrain, yTest, trainMap, testMap)

    # for each topic, do stratified K fold, and then merge them
    def topicStratifiedKFold(yTrain, trainMap, n_fold=3, randSeed=1):
        assert n_fold > 1
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
            topicyFoldNum[t] = { yClass: int(round(float(cnt)/n_fold)) for yClass, cnt in yNum.items() }
    
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
            if nowCnt[t][y] >= topicyFoldNum[t][y] and foldIndex[t][y] < n_fold - 1:
                foldIndex[t][y] += 1
                nowCnt[t][y] = 0 
            nowCnt[t][y] += 1
            testFold[i] = foldIndex[t][y]
        
        # making topicMapping for testing(validation) parts of instances
        foldTopicMap = [list() for i in range(0, n_fold)]
        for i, fi in enumerate(testFold):
            foldTopicMap[fi].append(trainMap[i])

        #print('yTrain:', yTrain)
        #print('trainMap:', trainMap)
        #print('testFold:', testFold)
        #print('foldTopicMap', foldTopicMap)
        return (PredefinedSplit(testFold), foldTopicMap)


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

