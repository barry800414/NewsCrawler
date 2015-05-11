
import sys
import json
from collections import defaultdict

def getTagCntOfWord(newsDict, sentSep=',', wordSep=' ', tagSep='/'):
    tagCnt = dict()
    for newsId, news in newsDict.items():
        for col in ['content_pos', 'title_pos']:
            for sent in news[col].split(sentSep):
                for wt in sent.split(wordSep):
                    wtSplit = wt.split(tagSep)
                    if len(wtSplit) != 2:
                        print(wt)
                        continue
                    else:
                        (w, t) = wtSplit
                    if w not in tagCnt:
                        tagCnt[w] = defaultdict(int)
                    tagCnt[w][t] += 1
    return tagCnt

def saveWordTag(tagCnt, topN=1, outfile=sys.stderr):
    for w in tagCnt.keys():
        t = sorted(tagCnt[w].items(), key=lambda x:x[1], reverse=True)
        print(w, end=':', file=outfile)
        for i in range(0, topN if topN < len(t) else len(t)):
            if i == 0:
                print(t[i][0], end='', file=outfile)
            else:
                print(' ' + t[i][0], end='', file=outfile)
        print('', file=outfile)

def loadWordTag(infile):
    wordTag = dict()
    tagWord = dict()
    for line in infile:
        entry = line.strip().split(':')
        assert len(entry) == 2
        word = entry[0]
        if word not in wordTag:
            wordTag[word] = set()
        entry = entry[1].split(' ')
        for tag in entry:
            if tag not in tagWord:
                tagWord[tag] = set()
            wordTag[word].add(tag)
            tagWord[tag].add(word)
    return (wordTag, tagWord)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'TaggedNewsJsonFile WordTagFile', file=sys.stderr)
        exit(-1)

    taggedNewsJsonFile = sys.argv[1]
    wordTagFile = sys.argv[2]

    with open(taggedNewsJsonFile, 'r') as f:
        newsDict = json.load(f)

    tagCnt = getTagCntOfWord(newsDict)
    with open(wordTagFile, 'w') as f:
        saveWordTag(tagCnt, outfile=f)
