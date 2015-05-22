
import sys
import json
from Lemmatizer import *

SENT_SEP=','

def lemmatizeTaggedCorpus(taggedNewsDict, cols=['content_pos'], sentSep=SENT_SEP):
    for newsId, news in taggedNewsDict.items():
        for col in cols:
            text = news[col]
            print(text)
            newText = ''
            for sent in text.split(sentSep):
                newSent = lemmatizeTaggedSent(sent)
                if len(newText) == 0:
                    newText = str(newSent)
                else:
                    newText = newText + sentSep + newSent
            news[col] = newText
            print(newText)
    return taggedNewsDict
            

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'InTaggedNewsJsonFile OutTaggedNewsJsonFile', file=sys.stderr)
        exit(-1)

    inTaggedNewsJsonFile = sys.argv[1]
    outTaggedNewsJsonFile = sys.argv[2]

    with open(inTaggedNewsJsonFile, 'r') as f:
        taggedNewsDict = json.load(f)

    taggedNewsDict = lemmatizeTaggedCorpus(taggedNewsDict)

    with open(outTaggedNewsJsonFile, 'w') as f:
        json.dump(taggedNewsDict, f, ensure_ascii=False, indent=1)


