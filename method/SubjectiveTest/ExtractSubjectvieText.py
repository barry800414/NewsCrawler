
import sys
import re
from misc import *
import Punctuation

def genRegexStr(tagList):
    outStr = '<('
    "<((?:a)|(?:o)|(?:ia)|(?:io))>(.+?)</\\1>"
    for i, tag in enumerate(tagList):
        if i == 0:
            outStr += '(?:%s)' % (tag)
        else:
            outStr += '|(?:%s)' % (tag)
    outStr += ')>(.+?)</\\1>'
    return outStr

def filterLabelNews(labelNewsList, tagList, topicList):
    newList = list()
    regexStr = genRegexStr(tagList)
    for labelNews in labelNewsList:
        if labelNews['statement_id'] not in topicList:
            continue
        content = labelNews['news']['content']
        texts = re.findall(regexStr, content)
        result = ''
        for tag, text in texts:
            result = putText(result, text)
        if len(result.strip()) != 0:
            labelNews['news']['content'] = result
            newList.append(labelNews)
    return newList


def putText(text, newText):
    #print('|' + newText + '|')
    if len(newText.strip()) == 0:
        return text
    else:
        if len(text) == 0:
            text = str(newText)
        else:
            text += " " + str(newText)
        return text

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'labelSubjectiveLabelNewsFile outFilterNewsFile', file=sys.stderr)
        exit(-1)

    labelNewsJsonFile = sys.argv[1]
    outFile = sys.argv[2]

    with open(labelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)

    tagList = ['a', 'ia', 'o', 'io']
    topicList = [4]

    newsIdSetInTopic = set([ ln['news_id'] for ln in labelNewsList if ln['statement_id'] in topicList ])

    labelNewsList = filterLabelNews(labelNewsList, tagList, topicList)
    newsIdSetHasLabel = set([ ln['news_id'] for ln in labelNewsList ])
    newsDict = { ln['news_id']: ln['news'] for ln in labelNewsList }
    print('#Original News:', len(newsIdSetInTopic))
    print('#News has subjective labels:', len(newsIdSetHasLabel))
    print('news id without any subjective lables:', newsIdSetInTopic - newsIdSetHasLabel)

    with open(outFile, 'w') as f:
        json.dump(newsDict, f, indent=2, ensure_ascii=False)

