
import math
from sklearn import svm, cross_validation, grid_search
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.metrics import accuracy_score
from eval import *

def trainAndTest(X_train, X_test, y_train, y_test, classifier='SVM', 
        scorer=None, prefix=None):
    if classifier == 'NaiveBayes':
        clf = MultinomialNB()
        clf.fit(X_train, y_train)
        
        yPredict = clf.predict(X_test)
        (accu, cm, macroF1, microF1, macroR) = evaluate(y_test, yPredict)
        
        print(prefix, 'testing', "MutinomialNB", "accuracy", accu, 
            macroF1, microF1, macroR, sep=',')

        #clf2 = GaussianNB()
        #clf2.fit(X_train, y_train)
        #print('testing', 'GaussianNB', clf2.score(X_test, y_test), sep=',')
        return 

    elif classifier == 'SVM':
        # grid search to find best parameters on training set
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
    clfGS = grid_search.GridSearchCV(clf, parameters, 
            scoring=scorer, refit=True, n_jobs=-1)

    clfGS.fit(X_train, y_train)
        
    #for gs in clfGS.grid_scores_:
        #print(prefix,'validation', gs[0], np.mean(gs[2]), sep=',')    

    # testing 
    yPredict = clfGS.predict(X_test)
    (accu, cm, macroF1, microF1, macroR) = evaluate(y_test, yPredict)

    print(prefix, 'testing', clfGS.best_params_, scorer, accu, 
            macroF1, microF1, macroR, sep=',')
    
def runExperiments(X, y, clfList=['NaiveBayes','SVM'], prefix=''):
    (X_train, X_test, y_train, y_test) = cross_validation.train_test_split(
            X, y, test_size=0.5, random_state=1)
    
    for clf in clfList:
        if clf == 'SVM':
            for scorer in [ "accuracy", macroF1Scorer, microF1Scorer, macroRScorer]:
                newPrefix = prefix + ",%s" % (clf)
                trainAndTest(X_train, X_test, y_train, y_test, clf, scorer, prefix=newPrefix)
        elif clf == 'NaiveBayes':
            newPrefix = prefix + ",%s" % (clf)
            trainAndTest(X_train, X_test, y_train, y_test, clf, prefix=newPrefix)

