#!/usr/bin/env python3
import sys
import json
import re
from NLPToolRequests import *

# default sentence separator
SEP = '[,;\t\n，。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！]'

# default new sentence separator
NEW_SEP = ','

# default to-removed punctuation
TO_REMOVE = '[\uF0D8\u0095/=&�+、:：／\|‧]'

# default brackets for fixing them (not to segment)
BRACKETS = [ ('[', ']'), ('(', ')'), ('{', '}'), 
             ('〈', '〉'), ('《', '》'), ('【', '】'),
             ('﹝', '﹞'), ('「','」'), ('『', '』'), 
             ('（','）'), ('〔','〕')]

allRelationSet = set()

# parse the news
def parseNews(news):
    news['title_dep'] = parseContent(news['title'])
    news['content_dep'] = parseContent(news['content'])
    return news

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def parseContent(content, sep=SEP, new_sep=NEW_SEP, 
        to_remove=TO_REMOVE, brackets=BRACKETS):
    result = list() 
    sArray = re.split(sep, content)
    for s in sArray:
        s2 = re.sub(to_remove, " ", s)
        s2 = s2.strip()
        if len(s2) > 0: #if empty string, skipped
            tmp = dict()
            tmp['originalSent'] = s2
            print(s2, end=' ')
            for c in s2:
                print(hex(ord(c)), end=' ')
            print('')
            tmp['typedDependencies'] = parseStr(s2) # an array of typed dependencies

            tds = tmp['typedDependencies']
            for td in tds:
                allRelationSet.add(td.split(" ")[0])

            result.append(tmp)
    return result

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage:', sys.argv[0], 'InNewsJson OutNewsJson', file=sys.stderr)
        exit(-1)
    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]
    with open(inNewsJsonFile, 'r') as f:
        labelNews = json.load(f)
    
    for i, n in enumerate(labelNews):
        parseNews(n['news'])
        if (i+1) % 10 == 0:
            print('Progress: (%d/%d)' % (i+1, len(labelNews)), file=sys.stderr)


    for reln in allRelationSet:
        print(reln)

    with open(outNewsJsonFile, 'w') as f:
        json.dump(labelNews, f, ensure_ascii=False, indent = 2)


