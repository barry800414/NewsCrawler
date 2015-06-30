#!/usr/bin/env python3
import sys, os, json
from collections import defaultdict

from sklearn.cross_validation import StratifiedKFold
from misc import *
from Volc import *

class Feature():
    # wvList: a list of word->value mapping 
    # volc: word -> index mapping
    def __init__(self, wvList, volc, name):
        self.name = name
        self.dim = len(volc)
        self.volc = volc
        self.docNum = len(wvList)
        self.wvList = wvList

    def getFeature(self, i):
        assert i < self.docNum
        f = { self.volc[w]:v for w,v in self.wvList[i].items() if w in self.volc }
        return f

    def getAllFeature(self):
        fList = [self.getFeature(i) for i in range(0, self.docNum)]
        return fList


# converting news to sentence features and document features
def genPolarityFeature(taggedLabelNewsList, volc=None, tfType='tf', allowedPOS=None,
        minCnt=5, sentSep=",", wordSep=" ", tagSep='/'):
    if volc is None:
        volc = Volc()
    print('Generating polarity features ... ', file=sys.stderr)
    numDoc = len(taggedLabelNewsList)
    # calculate word count in each sentence, sentTF[i][j] is j-th sent in i-th doc
    sentTF = [list() for i in range(0, numDoc)] 
    docTF = [defaultdict(int) for i in range(0, numDoc)]
    df = defaultdict(int)
    for i, taggedLabelNews in enumerate(taggedLabelNewsList):
        content = taggedLabelNews['news']['content_pos']
        wordSet = set()
        for sent in content.split(sentSep):
            stf = defaultdict(int)
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if w not in volc and volc.lockVolc:
                    continue
                if allowedPOS != None and t not in allowedPOS:
                    continue
                if w not in volc:
                    volc.addWord(w)
                docTF[i][w] += 1
                stf[w] += 1
                wordSet.add(w)
            sentTF[i].append(stf)
        for w in wordSet:
            df[w] += 1
        if (i+1) % 100 == 0:
            print('%cProgress:(%d/%d)' % (13, i+1, len(taggedLabelNewsList)), end='', file=sys.stderr)
    print('', file=sys.stderr)

    if tfType == 'tfidf':
        # get idf
        idf = getIDF(df, numDoc)
        # calc tfidf
        for tf in docTF:
            for w in tf.keys():
                tf[w] = tf[w] * idf[w]
        for tf in sentTF:
            for stf in tf:
                for w in stf.keys():
                    stf[w] = stf[w] * idf[w]

    if minCnt > 0:
        print('Removing words by document frequency < %d' % minCnt, end=': ', file=sys.stderr)
        print(len(volc), end='->', file=sys.stderr)
        DF = convertToWordIndexDF(df, volc)
        DF = volc.shrinkVolcByDocF(DF, minCnt)
        print(len(volc), file=sys.stderr)

    sentFList = [Feature(tf, volc, 'PolaritySentFeature') for tf in sentTF]
    docF = Feature(docTF, volc, 'PolarityDocFeature')
    return sentFList, docF

# converting news to sentence features and document features
def genSubjectiveFeature(taggedLabelNewsList, volc=None, tfType='tf', allowedPOS=None,
        minCnt=5, sentSep=",", wordSep=" ", tagSep='/'):
    if volc is None:
        volc = Volc()
    print('Generating subjective features ... ', file=sys.stderr)
    numDoc = len(taggedLabelNewsList)
    # calculate word count in each sentence, sentTF[i][j] is j-th sent in i-th doc
    sentTF = [list() for i in range(0, numDoc)] 
    df = defaultdict(int)
    for i, taggedLabelNews in enumerate(taggedLabelNewsList):
        content = taggedLabelNews['news']['content_pos']
        wordSet = set()
        for sent in content.split(sentSep):
            stf = defaultdict(int)
            for wt in sent.split(wordSep):
                (w, t) = wt.split(tagSep)
                if w not in volc and volc.lockVolc:
                    continue
                if allowedPOS != None and t not in allowedPOS:
                    continue
                if w not in volc:
                    volc.addWord(w)
                stf[w] += 1
                wordSet.add(w)
            sentTF[i].append(stf)
        for w in wordSet:
            df[w] += 1
        if (i+1) % 100 == 0:
            print('%cProgress:(%d/%d)' % (13, i+1, len(taggedLabelNewsList)), end='', file=sys.stderr)
    print('', file=sys.stderr)

    if tfType == 'tfidf':
        # get idf
        idf = getIDF(df, numDoc)
        # calc tfidf
        for tf in sentTF:
            for stf in tf:
                for w in stf.keys():
                    stf[w] = stf[w] * idf[w]

    if minCnt > 0:
        print('Removing words by document frequency < %d' % minCnt, end=': ',  file=sys.stderr)
        print(len(volc), end='->', file=sys.stderr)
        DF = convertToWordIndexDF(df, volc)
        DF = volc.shrinkVolcByDocF(DF, minCnt)
        print(len(volc), file=sys.stderr)

    sentFList = [Feature(tf, volc, "SubjectiveSentFeature") for tf in sentTF]
    return sentFList

# calcalating sentence subjectivie scores to guess inital sets
def countSentScore(sentFList):
    sentScoreList = list()
    for di, sentF in enumerate(sentFList):
        # (i, sum of subjective words)
        sentScore = [(i, sum(sentF.getFeature(i).values())) for i in range(0, sentF.docNum)]
        sentScoreList.append(sentScore)
    return sentScoreList

def findTopSent(sentScoreList, percent):
    sentIndexList = list()
    for di, sentScore in enumerate(sentScoreList):
        sentScore.sort(key=lambda x:x[1], reverse=True)
        topNum = round(len(sentScore) * percent) 
        sentIndex = sorted([sentScore[i][0] for i in range(0, topNum)])
        sentIndexList.append(sentIndex)
    return sentIndexList

def convertToWordIndexDF(df, volc):
    DF = defaultdict(int)
    for w, cnt in df.items():
        DF[volc[w]] += cnt
    return DF

def getIDF(df, numDoc):
    idf = dict()
    for w, f in df.items():
        idf[w] = math.log(float(numDoc + 1) / (f + 1))
    return idf

# print data for sle struct svm tool
def printDataFile(filename, labels, pSentFList, pDocF, sSentFList, indexList):
    assert len(pSentFList) == len(sSentFList)
    with open(filename, 'w') as outfile:
        for di in indexList:
            assert pSentFList[di].docNum == sSentFList[di].docNum
            nSent = pSentFList[di].docNum
            # label and sentence number
            label = 1 if labels[di] == 1 else -1
            print(label, nSent, sep=' ', file=outfile)
            for si in range(0, nSent):
                print(si, end='', file=outfile)
                # polarity feature
                pf = pSentFList[di].getFeature(si)
                for i, v in sorted(pf.items(), key=lambda x:x[0]):
                    print(' ', i+1, ':', v, sep='', end='', file=outfile)    
                    
                # subjective feature
                sf = sSentFList[di].getFeature(si)
                for i, v in sorted(sf.items(), key=lambda x:x[0]):
                    print(' S', i+1, ':', v, sep='', end='', file=outfile)
                print('', file=outfile)
            # document feature
            pdf = pDocF.getFeature(di)
            print(nSent, end='',file=outfile)
            for i, v in sorted(pdf.items(), key=lambda x:x[0]):
                print(' ', i+1, ':', v, sep='', end='', file=outfile)
            print('\n', file=outfile)

def printInitGuessFile(filename, sentIndexList, trainIndex):
    with open(filename, 'w') as outfile:
        for i in trainIndex:
            sentIndex = sentIndexList[i]
            print(len(sentIndex), end='', file=outfile)
            for j, si in enumerate(sentIndex):
                print(' ', si, sep='', end='', file=outfile)
            print('', file=outfile)

if __name__ == '__main__':
    if len(sys.argv) != 5:
        print('Usage:', sys.argv[0], 'TaggedLabelNewsJsonFile SubjectiveWord Seed GuessPercent', file=sys.stderr)
        exit(-1)

    taggedLabelNewsJsonFile = sys.argv[1]
    subjectiveWordFile = sys.argv[2]
    seed = int(sys.argv[3])
    percent = float(sys.argv[4])

    # load model config
    # read in tagged news json file
    with open(taggedLabelNewsJsonFile, 'r') as f:
        lnList = json.load(f)
    lnListInTopic = divideLabelNewsByTopic(lnList)
    sVolc = Volc()
    sVolc.load(subjectiveWordFile)
    sVolc.lock()

    allowedPOS = set(['VV', 'VA', 'JJ', 'NN', 'NR', 'AD'])
    minCnt = 5

    for t, lns in sorted(lnListInTopic.items(), key=lambda x:x[0]):
        newVolc = sVolc.copy()
        sSentFList = genSubjectiveFeature(lns, volc=newVolc, tfType='tf', allowedPOS=allowedPOS, minCnt=0)
        newVolc.unlock()
        pSentFList, pDocF = genPolarityFeature(lns, volc=newVolc, tfType='tf', allowedPOS=allowedPOS, minCnt=minCnt)
        sentIndexList = findTopSent(countSentScore(sSentFList), percent)
        labels = getLabels(lns)
        y = np.array(labels)
        kfold = StratifiedKFold(y, n_folds=10, shuffle=True, random_state=seed)
        for i, (trainIndex, testIndex) in enumerate(kfold):
            prefix = 'T%dS%dF%d' % (t, seed, i)
            os.system('mkdir -p %s' % (prefix))

            # generate validation data
            yTrain = y[trainIndex]
            valKfold = StratifiedKFold(yTrain, n_folds=10, shuffle=True, random_state=seed)
            for j, (valTrainIndex, valTestIndex) in enumerate(valKfold):
                realTrainIndex = [trainIndex[i] for i in valTrainIndex]
                realTestIndex = [trainIndex[i] for i in valTestIndex]
                prefix2 = '%s/%sV%d' % (prefix, prefix, j)
                printDataFile('%s.train' % (prefix2), y, pSentFList, pDocF, sSentFList, realTrainIndex)
                printDataFile('%s.test' % (prefix2), y, pSentFList, pDocF, sSentFList, realTestIndex)
                printInitGuessFile('%s.init' % (prefix2), sentIndexList, realTrainIndex)

            # generate training and testing data
            printDataFile('%s/%s.train' % (prefix, prefix), y, pSentFList, pDocF, sSentFList, trainIndex)
            printDataFile('%s/%s.test' % (prefix, prefix), y, pSentFList, pDocF, sSentFList, testIndex)
            printInitGuessFile('%s/%s.init' % (prefix, prefix), sentIndexList, trainIndex)

