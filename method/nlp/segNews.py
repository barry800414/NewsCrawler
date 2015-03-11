#!/usr/bin/env python3
import sys
import json
import re
from NLPToolRequests import *

# default sentence separator
SEP = '[,;\t\n，。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！\u2019]'

# default new sentence separator
NEW_SEP = ','

# default to-removed punctuation
TO_REMOVE = '[\uF0D8\u0095/=&�+、:：／\|‧]'

# default brackets for fixing them (not to segment)
BRACKETS = [ ('[', ']'), ('(', ')'), ('{', '}'), 
             ('〈', '〉'), ('《', '》'), ('【', '】'),
             ('﹝', '﹞'), ('「','」'), ('『', '』'), 
             ('（','）'), ('〔','〕')]

# segment the news(title & content) & statement
def segLabelNews(newsDict):
    newsDict['title_seg'] = segText(newsDict['title'])
    newsDict['content_seg'] = segText(newsDict['content'])
    return newsDict

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def segText(content, sep=SEP, new_sep=NEW_SEP, 
        to_remove=TO_REMOVE, brackets=BRACKETS):
    segText = ''

    # deal with brackets TODO
    '''
    fixedPairs = list()
    for b in brackets:
        regexStr = "%s(.*?)%s" % (b[0], b[1])
        matchObj = re.finditer(regexStr, content)
        for m in matchObj:
            fixedPairs.append((m.start(), m.end()))
    
    if isOverlapping(fixedPairs):
        print('Overlapping!')
        return None
    '''
    sArray = re.split(sep, content)
    for s in sArray:
        s2 = s.strip()
        if len(s2) == 0: #if empty string, skip it
            continue
        
        print('|%s|' % (s2))
        # segment the string by Stanford NLP segmenter
        result = segmentStr(s2)
        # remove punctuation
        result = re.sub(to_remove, '', result) 
        # normalizing spaces (N -> 1 space char)
        result = re.sub('[ ]+', ' ', result)
        # remove delimeter chars in front/end of string
        result = result.strip()
        print('|%s|' % result)
        if len(result) == 0:
            continue
        if len(segText) != 0:
            segText += NEW_SEP + result
        else:
            segText += result
    return segText

# brute force way
def isOverlapping(intervals):
    for i in range(0, len(intervals)):
        s = intervals[i][0]
        e = intervals[i][1]
        for j in range(i+1, len(intervals)):
            s2 = intervals[j][0]
            e2 = intervals[j][1]
            if (s >= s2 and s <= e2) or (e >= s2 and e <= e2):
                return True
    return False

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'InNewsJson OutNewsJson', file=sys.stderr)
        exit(-1)
    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]
    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)
    
    cnt = 0
    for newsId, news in newsDict.items():
        segLabelNews(news)
        cnt =+ 1
        if cnt % 10 == 0:
            print('Progress: (%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)

    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent = 2)


