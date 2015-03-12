
import sys
from sklearn.metrics import confusion_matrix, f1_score, recall_score, accuracy_score, make_scorer

def evaluate(yTrue, yPredict, printInfo=False, outfile=sys.stderr):
 
    # accuracy 
    accu = accuracy_score(yTrue, yPredict)
    if printInfo:
        print('Accuracy:', accu, file=outfile)

    # confusion matrix
    cm = confusion_matrix(yTrue, yPredict)
    if printInfo:
        print('confusion matrix:\n', cm, file=outfile)
    
    # f1 scores
    macroF1 = f1_score(yTrue, yPredict, average='macro')
    microF1 = f1_score(yTrue, yPredict, average='micro')
    if printInfo:
        print('Macro F1:', macroF1, '\tMicro F1:', microF1, file=outfile)
    
    # average recall (macro - recall
    macroR = recall_score(yTrue, yPredict, average='macro')
    if printInfo:
        print('Average Recall:', macroR, file=outfile)

    return (accu, cm, macroF1, microF1, macroR)

cmScorer = make_scorer(confusion_matrix)
macroF1Scorer = make_scorer(f1_score, average='macro')
microF1Scorer = make_scorer(f1_score, average='micro')
macroRScorer = make_scorer(recall_score, average='macro')


def topicEval(yTrue, yPredict, topicMapping, printInfo=False, outfile=sys.stderr):
    topicSet = set()
    for t in topicMapping:
        topicSet.add(t)
    
    yTrueInTopic = {t:list() for t in topicSet}
    yPredictInTopic = {t:list() for t in topicSet}
    
    for i, t in enumerate(topicMapping):
        yTrueInTopic[t].append(yTrue[i])
        yPredictInTopic[t].append(yPredict[i])
        
    rForEachTopic = dict()
    for t in topicSet:
        if len(yTrueInTopic[t]) == 0 or len(yPredictInTopic) == 0:
            rForEachTopic[t] = None #FIXME
        else:
            r = (yTrueInTopic[t], yPredictInTopic[t])
            rForEachTopic[t] = r

    return rForEachTopic

def avgTopicResults(fForEachTopic):
    #TODO
    pass

