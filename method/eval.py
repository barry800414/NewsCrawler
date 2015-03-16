
import sys
import numpy as np
from sklearn.metrics import confusion_matrix, f1_score, recall_score, accuracy_score, make_scorer

cmScorer = make_scorer(confusion_matrix)
macroF1Scorer = make_scorer(f1_score, average='macro')
microF1Scorer = make_scorer(f1_score, average='micro')
macroRScorer = make_scorer(recall_score, average='macro')

scorerMap = {"accuracy" : "accuracy", "macroF1": macroF1Scorer, "microF1": microF1Scorer, 
        "macroR": macroRScorer } 

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
    #print(yTrue)
    #print(yPredict)
    macroF1 = f1_score(yTrue, yPredict, average='macro')
    microF1 = f1_score(yTrue, yPredict, average='micro')
    if printInfo:
        print('Macro F1:', macroF1, '\nMicro F1:', microF1, file=outfile)
    
    # average recall (macro - recall
    macroR = recall_score(yTrue, yPredict, average='macro')
    if printInfo:
        print('Average Recall:', macroR, file=outfile)

    return (accu, cm, macroF1, microF1, macroR)

# evaluation for each topic 
def topicEval(yTrue, yPredict, topicMapping, printInfo=False, outfile=sys.stderr):
    assert len(yTrue) == len(yPredict)
    length = len(yTrue)

    # find all possible topic
    topicSet = set()
    for t in topicMapping:
        topicSet.add(t)
    
    # divide yTrue and yPredict
    yTrueInTopic = {t:list() for t in topicSet}
    yPredictInTopic = {t:list() for t in topicSet}
    
    for i, t in enumerate(topicMapping):
        yTrueInTopic[t].append(yTrue[i])
        yPredictInTopic[t].append(yPredict[i])
    
    for t in topicSet:
        yTrueInTopic[t] = np.array(yTrueInTopic[t])
        yPredictInTopic[t] = np.array(yPredictInTopic[t])

    # evaluation for each topic
    rForEachTopic = dict()
    for t in topicSet:
        if len(yTrueInTopic[t]) == 0 or len(yPredictInTopic) == 0:
            rForEachTopic[t] = None
        else:
            if printInfo:
                print('\n>>>>>>>>>>>>>>>Topic %d<<<<<<<<<<<<<<<' % t, file=outfile)
            r = evaluate(yTrueInTopic[t], yPredictInTopic[t], printInfo=printInfo, outfile=outfile)
            rForEachTopic[t] = r
    
    # calculate average metric for all topics
    if printInfo:
        print('\n>>>>>>>>>>>>>>>Topic Average<<<<<<<<<<<<<<<', file=outfile)
    weight = { t: float(len(yTrueInTopic[t]))/length for t in topicSet }
    avgR = avgTopicResults(rForEachTopic, weight, printInfo=printInfo, outfile=outfile)

    return (rForEachTopic, avgR)

def avgTopicResults(rForEachTopic, weight, printInfo=False, outfile=sys.stderr):
    if rForEachTopic == None or len(rForEachTopic) == 0:
        return None
    avgAccu = 0.0
    avgMacroF1 = 0.0
    avgMicroF1 = 0.0
    avgMacroR = 0.0
    cnt = 0
    for t, r in rForEachTopic.items():
        if r != None:
            avgAccu += weight[t] * r[0]
            avgMacroF1 += weight[t] * r[2]
            avgMicroF1 += weight[t] * r[3]
            avgMacroR += weight[t] * r[4]
            cnt += 1
    if cnt != 0:
        if printInfo:
            print('avgAccu:', avgAccu, file=outfile)
            print('avgMacroF1:', avgMacroF1, file=outfile)
            print('avgMicroF1:', avgMicroF1, file=outfile)
            print('avgMacroR:', avgMacroR, file=outfile)
            print('Cnt:', cnt, file=outfile)
        return (avgAccu, avgMacroF1, avgMicroF1, avgMacroR)
    else:
        if printInfo:
            print('None', file=outfile)
        return None

def writeResult(yTrue, yPredict, topicMapping, fout):
    assert len(yTrue) == len(yPredict) and len(yPredict) == len(topicMapping)
    print('yTrue, yPredict, topicId', file=fout)
    for i in range(0, len(yTrue)):
        print(yTrue[i], yPredict[i], topicMapping[i], sep=',', file=fout)
    return 

def readResult(filename):
    yTrue = list()
    yPredict = list()
    topicMapping = list()
    with open(filename, 'r') as f:
        f.readline()
        for line in f:
            entry = line.split(',')
            yTrue.append(int(entry[0]))
            yPredict.append(int(entry[1]))
            topicMapping.append(int(entry[2]))

    return (yTrue, yPredict, topicMapping)
