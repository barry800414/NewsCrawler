
import sys
import json
from Lemmatizer import *

SENT_SEP=','

def lemmatizeTaggedCorpus(taggedNewsDict, cols=['content_pos'], sentSep=SENT_SEP):
    newNewsDict = dict()
    cnt = 0
    for newsId, news in sorted(taggedNewsDict.items()):
        for col in cols:
            text = news[col]
            newText = ''
            for sent in text.split(sentSep):
                newSent = lemmatizeTaggedSent(sent)
                if len(newText) == 0:
                    newText = str(newSent)
                else:
                    newText = newText + sentSep + newSent
            news[col] = newText
        newNewsDict[newsId] = news 
        cnt = cnt + 1
        if (cnt + 1) % 10 == 0:
            print('%cProgress: (%d/%d)' % (13, cnt+1, len(taggedNewsDict)), end='', file=sys.stderr)
    print('',file=sys.stderr)
    return newNewsDict

def lemmatizeDepParsedCorpus(depParsedNewsDict, cols=['content_dep']):
    newNewsDict = dict()
    cnt = 0 
    for newsId, news in sorted(depParsedNewsDict.items()):
        for col in cols:
            depList = news[col]
            for dep in depList:
                tdList = dep['tdList']
                newTdList = list()
                for line in tdList:
                    newLine = lemmatizeTdLine(line)
                    newTdList.append(newLine)
                dep['tdList'] = newTdList
        newNewsDict[newsId] = news
        cnt = cnt + 1
        if (cnt + 1) % 10 == 0:
            print('%cProgress: (%d/%d)' % (13, cnt+1, len(depParsedNewsDict)), end='', file=sys.stderr)
    print('',file=sys.stderr)
    return newNewsDict


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'InNewsJsonFile OutNewsJsonFile tag/dep/const', file=sys.stderr)
        exit(-1)

    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]
    taskType = sys.argv[3]

    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)

    if taskType == 'tag':
        newsDict = lemmatizeTaggedCorpus(newsDict)
    elif taskType == 'dep':
        newsDict = lemmatizeDepParsedCorpus(newsDict)

    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent=1)


