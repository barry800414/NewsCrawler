#!/usr/bin/env python3
#!/usr/bin/env python3
import sys
import json
import re
from NLPToolRequests import *

# default sentence separator
SEP = '[.,\t\n，。　「」﹝﹞【】\[\]]'

# default new sentence separator
NEW_SEP = ','

# default brackets for fixing them (not to segment)
BRACKETS = [ ('[', ']'), ('(', ')'), ('{', '}'), 
             ('〈', '〉'), ('《', '》'), ('【', '】'),
             ('﹝', '﹞'), ('「','」'), ('『', '』') ]

# segment the news
def segNews(news):
    news['title_seg'] = segContent(news['title'])
    news['content_seg'] = segContent(news['content'])
    return news

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def segContent(content, sep=SEP, new_sep=NEW_SEP, brackets=BRACKETS):
    segContent = ''

    # deal with brackets
    fixedPairs = list()
    for b in brackets:
        regexStr = "%s(.*?)%s" % (b[0], b[1])
        matchObj = re.finditer(regexStr, content)
        for m in matchObj:
            fixedPairs.append((m.start(), m.end()))
    
    if isOverlapping(fixedPairs):
        print('Overlapping!')
        return None
    
    sArray = re.split(sep, content)
    for s in sArray:
        s2 = s.strip()
        if len(s2) > 0: #if empty string, skipped
            result = segmentStr(s)
            segContent += result + NEW_SEP
    return segContent

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
    if len(sys.argv) != 2:
        print('Usage:', sys.argv[0], 'newsJson', file=sys.stderr)
        exit(-1)
    newsJsonFile = sys.argv[1]
    with open(newsJsonFile, 'r') as f:
        news = json.load(f)
    
    for n in news[0:1]:
        segNews(n['news'])
        print(n['news'])
