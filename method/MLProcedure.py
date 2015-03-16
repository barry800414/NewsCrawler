
import math
import random
from collections import defaultdict

from sklearn import svm, cross_validation, grid_search
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from eval import *
from misc import *

def trainAndTest(XTrain, XTest, yTrain, yTest, testMap=None, classifier='SVM', 
        scorerName=None, prefix=None):
    if classifier == 'NaiveBayes':
        clf = MultinomialNB()
        clf.fit(XTrain, yTrain)
        
        yPredict = clf.predict(XTest)
        if testMap == None:
            (accu, cm, macroF1, microF1, macroR) = evaluate(yTest, yPredict)
        else:
            (rForEachTopic, avgR) = topicEval(yTest, yPredict, testMap, printInfo=False)
            accu = avgR[0]
            macroF1 = avgR[1]
            microF1 = avgR[2]
            macroR = avgR[3]

        print(prefix, 'testing', "MutinomialNB", "accuracy", accu, 
                macroF1, microF1, macroR, sep=',')
        return 

    elif classifier == 'MaxEnt' or classifier == 'LogReg':
        parameters = {
            'penalty': ('l1', 'l2'),
            'C': [0.5, 1, 2],
        }
        clf = LogisticRegression()
        print('test')
        
    elif classifier == 'SVM':
        C = [math.pow(2, i) for i in range(-1,11,2)]
        gamma = [math.pow(2, i) for i in range(-11,-1,2)]
        parameters = {
                'kernel': ('rbf', 'linear'), 
                'C': C, 
                'gamma': gamma
            }
        clf = svm.SVC()
    
    elif classifier == 'RandomForest': #depricated: RF does not support sparse matrix
        estNum = [5, 10, 15, 20]
        minSampleSplit = [1, 2]
        parameters = {
                "n_estimators": estNum,
                "min_samples_split": minSampleSplit
            }
        clf = RandomForestClassifier()
    
    # if not naive Bayes:
    kfold = cross_validation.StratifiedKFold(yTrain, n_folds=2)
    clfGS = grid_search.GridSearchCV(clf, parameters, scoring=scorerMap[scorerName], 
            refit=True, cv=kfold, n_jobs=-1)

    clfGS.fit(XTrain, yTrain)
        
    # testing 
    yPredict = clfGS.predict(XTest)
    if testMap == None:
        (accu, cm, macroF1, microF1, macroR) = evaluate(yTest, yPredict)
    else:
        (rForEachTopic, avgR) = topicEval(yTest, yPredict, testMap, printInfo=False)
        accu = avgR[0]
        macroF1 = avgR[1]
        microF1 = avgR[2]
        macroR = avgR[3]

    print(prefix, 'testing', dict2Str(clfGS.best_params_), scorerName, accu, 
            macroF1, microF1, macroR, sep=',')
    
def runExperiments(X, y, topicMapping=None, clfList=['NaiveBayes','SVM'], prefix=''):
    #TODO: use different seed
    (XTrain, XTest, yTrain, yTest, trainMap, testMap) = StratifiedTrainTestSplit(X, y, 
            topicMapping, test_size=0.5, random_state=1)
    
    for clf in clfList:
        if clf in ['SVM', 'MaxEnt', 'LogReg'] :
            for scorerName in ['accuracy', 'macroF1', 'microF1', 'macroR']:
                newPrefix = prefix + ",%s" % (clf)
                trainAndTest(XTrain, XTest, yTrain, yTest, testMap, clf, scorerName, prefix=newPrefix)
        elif clf == 'NaiveBayes':
            newPrefix = prefix + ",%s" % (clf)
            trainAndTest(XTrain, XTest, yTrain, yTest, testMap, clf, prefix=newPrefix)
  
#Deprecated: there could be 0 instance in testing data
def trainTestSplit(X, y, topicMapping=None, test_size=0.5, random_state=0):
    assert X.shape[0] == len(y)
    assert test_size > 0.0 and test_size < 1.0
    length = len(y)
    index = [i for i in range(0, length)]
    random.seed(random_state)
    random.shuffle(index)
    
    testNum = int(math.ceil(test_size * length))
    trainNum = length - testNum

    XTrain = X[[i for i in index[0:trainNum]]]
    XTest = X[[i for i in index[trainNum:]]]
    yTrain = y[[i for i in index[0:trainNum]]]
    yTest = y[[i for i in index[trainNum:]]]
    
    if topicMapping != None:
        assert length == len(topicMapping)
        trainMap = [topicMapping[i] for i in index[0:trainNum]]
        testMap = [topicMapping[i] for i in index[trainNum:]]
        return (XTrain, XTest, yTrain, yTest, trainMap, testMap)
    else:
        return (XTrain, XTest, yTrain, yTest, None, None)

# In order to prevent 0 cases in training or testing data (s.t. evaluation 
# metric is illed-defined), we first get the expected number of instance first
def StratifiedTrainTestSplit(X, y, topicMapping=None, test_size=0.5, random_state=0):
    assert X.shape[0] == len(y)
    assert test_size > 0.0 and test_size < 1.0
    length = len(y)

    # count the number of instance for each y class
    yNum = defaultdict(int)
    for i in range(0, length):
        yNum[y[i]] += 1

    # calculate expected number of instance for each class
    yTestNum = { yi: int(math.ceil(cnt*test_size)) for yi, cnt in yNum.items() }
    yTrainNum = { yi: yNum[yi] - yTestNum[yi] for yi in yNum.keys() }
    

    index = [i for i in range(0, length)]
    random.seed(random_state)
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
    
    ''' 
    print('y:', yNum)
    yNum = defaultdict(int)
    for yi in yTrain:
        yNum[yi] += 1
    print('yTrain:', yNum)
    yNum = defaultdict(int)
    for yi in yTest:
        yNum[yi] += 1
    print('yTest:', yNum)
    '''

    if topicMapping != None:
        assert length == len(topicMapping)
        trainMap = [topicMapping[i] for i in trainIndex]
        testMap = [topicMapping[i] for i in testIndex]
        return (XTrain, XTest, yTrain, yTest, trainMap, testMap)
    else:
        return (XTrain, XTest, yTrain, yTest, None, None)
    
