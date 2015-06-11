
import sys
import re
from misc import *
import Punctuation

def checkOccur(string, sentiDict):
    for w in sentiDict.keys():
        if string.find(w) != -1:
            #print(string, w)
            return True
    return False

def calcPRF1(tp, fn, fp):
    p = r = f1 = None
    if (tp + fp) != 0:
        p = float(tp) / (tp + fp)
    if (tp + fn) != 0:
        r = float(tp) / (tp + fn)
    if p != None and r != None and p + r != 0:
        f1 = 2 * p * r / (p + r)
    return (p, r, f1)


def printTagStat(label, labelNewsList, indexList, tagList, sepRegexStr):
    avgSentRate = {tag: 0.0 for tag in tagList}
    for i in indexList:
        ln = labelNewsList[i]
        content = ln['news']['content']

        #print('Document: ', ln['news_id'])
        # calculate #sentences in tags
        sentRate = {tag:0.0 for tag in tagList}
        for tag in tagList:
            texts = re.findall('<%s>(.+?)</%s>' % (tag, tag), content)
            #if len(texts) != 0:
            #    print(texts)
            for text in texts:
                if len(text.strip()) == 0:
                    continue
                sArray = re.split(sepRegexStr, text)
                for sent in sArray:
                    if len(sent.strip()) != 0:
                        sentRate[tag] += 1
        # calculate total sentence number
        sArray = re.split(sepRegexStr, content)
        totalNum = 0
        for sent in sArray:
            if len(sent.strip()) != 0:
                totalNum += 1
        #print('totalNum:', totalNum) 
        for tag in tagList:
            sentRate[tag] /= totalNum
            avgSentRate[tag] += sentRate[tag]
        #print(sum(sentRate.values()))

    for tag in tagList:
        avgSentRate[tag] /= len(indexList)

    print(label, avgSentRate['a'], avgSentRate['ia'], avgSentRate['o'], avgSentRate['io'], 
            avgSentRate['a'] + avgSentRate['o'], avgSentRate['ia'] + avgSentRate['io'], sep=',')


def locateSentencesInTag(content, tagList, sentiDict, sepRegexStr):
    tp = { tag:0 for tag in tagList }
    fn = { tag:0 for tag in tagList }
    for tag in tagList:
        texts = re.findall('<%s>(.+?)</%s>' % (tag, tag), content)
        if len(texts) != 0:
            print(texts)
        for text in texts:
            if len(text.strip()) == 0:
                continue
            sArray = re.split(sepRegexStr, text)
            for sent in sArray:
                if len(sent.strip()) == 0:
                    #fn[tag] += 1
                    continue
                if checkOccur(sent, sentiDict):
                    tp[tag] += 1
                else:
                    fn[tag] += 1
    return (tp, fn)

def locateSentencesOutsideTag(content, tagList, sentiDict, sepRegexStr):
    fp = { tag:0 for tag in tagList }
    tn = { tag:0 for tag in tagList }
    
    contentNotInTag = content
    for tag in tagList:
        contentNotInTag = re.sub('<%s>(.+?)</%s>' % (tag, tag), " ", contentNotInTag)
    sArray = re.split(sepRegexStr, contentNotInTag)
    for sent in sArray:
        if len(sent.strip()) == 0:
            continue
        if checkOccur(sent, sentiDict):
            for tag in tagList:
                fp[tag] += 1
        else:
            for tag in tagList:
                tn[tag] += 1

    return (fp, tn)

# printing the statistic information of locating sentences with opinions
def printLocatingStat(labelNewsList, indexList, tagList, sentiDict, sepRegexStr):
    avgHitRate = 0.0
    avgRelRate = { tag: 0.0 for tag in tagList }
    avgP = { tag: 0.0 for tag in tagList }
    avgR = { tag: 0.0 for tag in tagList }
    avgF1 = { tag: 0.0 for tag in tagList }
    pCnt = { tag: 0 for tag in tagList }
    rCnt = { tag: 0 for tag in tagList }
    f1Cnt = { tag: 0 for tag in tagList }

    for i in indexList:
        ln = labelNewsList[i]
        content = ln['news']['content']

        # for the text in tags
        (tp, fn) = locateSentencesInTag(content, tagList, sentiDict, sepRegexStr)

        # for the text not in tags
        (fp, tn) = locateSentencesOutsideTag(content, tagList, sentiDict, sepRegexStr)

        #print('Document: ', ln['news_id'])
        for tag in tagList:
            (p, r, f1) = calcPRF1(tp[tag], fn[tag], fp[tag])
            relRate = (tp[tag] + fn[tag]) / (tp[tag] + fn[tag] + fp[tag] + tn[tag])
            #print('totalCnt:', (tp[tag] + fn[tag] + fp[tag] + tn[tag]))
            #print('relRate:', relRate)
            #print('tag %s:\n-----------------------' % (tag))
            #print('\thit\tno hit')
            #print(' rel\t%d\t%d ' % (tp[tag], fn[tag]))
            #print('irrel\t%d\t%d ' % (fp[tag], tn[tag]))
            #print('relevant rate:', relRate)
            #print('Precision:', p, 'Recall:', r, 'F1:', f1)
            #print('-----------------------')
            if p != None:
                avgP[tag] += p
                pCnt[tag] += 1
            if r != None:
                avgR[tag] += r
                rCnt[tag] += 1
            if f1 != None:
                avgF1[tag] += f1
                f1Cnt[tag] += 1
            avgRelRate[tag] += relRate
        
        hitRate =  (tp[tag] + fp[tag]) / (tp[tag] + fp[tag] + fn[tag] + tn[tag])
        avgHitRate += hitRate
        #print('hitRate:', hitRate, '\n')
        

    # avgRelRate: average rate of sentences which express opinions
    # avgP: average precicion of locating sentences by lexicon
    # avgR: average recall of locating sentences by lexicon
    # avgF1: average f1 of locating sentences by lexicon
    # avgHitRate: average hit(predict the sentence as a opinion sentence) rate
    
    print('tag, Precision, Recall, F1-score, avgRelRate')
    for tag in tagList:
        if pCnt[tag] != 0:
            avgP[tag] = avgP[tag] / pCnt[tag]
        else:
            avgP[tag] = None
        if rCnt[tag] != 0:
            avgR[tag] = avgR[tag] / rCnt[tag]
        else:
            avgR[tag] = None
        if f1Cnt[tag] != 0:
            avgF1[tag] = avgF1[tag] / f1Cnt[tag]
        else:
            avgF1[tag] = None
        avgRelRate[tag] /= len(indexList)
        print(tag, avgP[tag], avgR[tag], avgF1[tag], avgRelRate[tag], sep=',')
    avgHitRate /= len(indexList) 
    print('avgHitRate:', avgHitRate)
    

def getIndexOfLabelNewsWithLabel(labelNewsList, tagList):
    indexDict = { "agree": list(), "oppose": list(), "neutral": list() }
    labeledNewsNum = 0 
    for i, ln in enumerate(labelNewsList):
        if ln['statement_id'] != 4:
            continue
        content = ln['news']['content']
        label = ln['label']
        labeled = False
        for tag in tagList:
            cnt1 = content.count('<' + tag + '>')
            if cnt1 > 0:
                labeled = True
            cnt2 = content.count('</' + tag + '>')

            if cnt1 != cnt2:
                print(ln['news_id'])
                print('#Tag <%s>: %d' % (tag, cnt1))
                print('#Tag </%s>: %d' % (tag, cnt2))
        if labeled:
            labeledNewsNum += 1
            indexDict[label].append(i)
    print('#labeled news:', labeledNewsNum)
    return indexDict

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'labelSubjectiveLabelNewsFile lexiconFile PunctuationFile', file=sys.stderr)
        exit(-1)

    labelNewsJsonFile = sys.argv[1]
    lexiconFile = sys.argv[2]
    punctFile = sys.argv[3]

    with open(labelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    sentiDict = readSentiDict(lexiconFile)
    with open(punctFile, 'r') as f:
        punct = json.load(f)

    sepRegexStr = Punctuation.toRegexStr(punct['sep'])

    tagList = ['a', 'ia', 'o', 'io']
    
    # find news with tags
    indexDict = getIndexOfLabelNewsWithLabel(labelNewsList, tagList)


    #print('label, <a>, <ia>, <o>, <io>, explicit, implicit')
    allIndex = list()
    for label, indexList in indexDict.items():
        printTagStat(label, labelNewsList, indexList, tagList, sepRegexStr)
        allIndex.extend(indexList)

    #print('---------------------')
    #printLocatingStat(labelNewsList, allIndex, tagList, sentiDict, sepRegexStr)



