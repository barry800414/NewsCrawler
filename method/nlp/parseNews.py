#!/usr/bin/env python3
import sys
import json
import re
import random
from NLPToolRequests import *

# default sentence separator
#SEP = '[;\t\n。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！]'

SEP = '[,;\t\n，。；　「」﹝﹞【】《》〈〉（）〔〕『 』\(\)\[\]!?？！]'

# default new sentence separator
NEW_SEP = ','

# default to-removed punctuation
TO_REMOVE = '[\uF06E\uF0D8\u0095/=&�+:：／\|‧]'
#TO_REMOVE = '[\uF0D8\u0095/=&�+、:：／\|‧]'

# default brackets for fixing them (not to segment)
BRACKETS = [ ('[', ']'), ('(', ')'), ('{', '}'), 
             ('〈', '〉'), ('《', '》'), ('【', '】'),
             ('﹝', '﹞'), ('「','」'), ('『', '』'), 
             ('（','）'), ('〔','〕')]

allRelationSet = set()

# parse the news
def depParseNews(news, draw=False, fileFolder=None):
    news['title_dep'] = depParseText(news['title'], draw=draw, 
            fileFolder=fileFolder, fileName='title')
    news['content_dep'] = depParseText(news['content'], draw=draw, 
            fileFolder=fileFolder, fileName='content')
    return news

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def depParseText(text, draw=False, fileFolder=None, fileName='', 
        sep=SEP, new_sep=NEW_SEP, to_remove=TO_REMOVE, brackets=BRACKETS):
    result = list() 
    sentArray = re.split(sep, text)
    
    # for each sentence
    for i, sent in enumerate(sentArray):
        cleanSent = re.sub(to_remove, " ", sent)
        cleanSent = cleanSent.strip()
        if len(cleanSent) > 0: #if empty string, skipped
            tmp = dict()
            tmp['sent'] = cleanSent
            # for debugging
            '''
            print(cleanSent, end=' ')
            for c in cleanSent:
                print(hex(ord(c)), end=' ')
            print('')
            '''
            # parse the sentence, return an array of typed dependencies
            (tmp['seg_sent'], tmp['tdList']) = sendDepParseRequest(cleanSent, 
                    draw=draw, fileFolder=fileFolder, 
                    fileName=fileName+"_%04d_%s" %(i,cleanSent),
                    returnTokenizedSent=True)

            # for debugging
            for td in tmp['tdList']:
                #print(td)
                allRelationSet.add(td.split(" ")[0])
            result.append(tmp)
    return result


# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def constParseText(text, sep=SEP, new_sep=NEW_SEP, to_remove=TO_REMOVE, 
        brackets=BRACKETS):
    result = list() 
    sentArray = re.split(sep, text)
    
    # for each sentence
    for i, sent in enumerate(sentArray):
        cleanSent = re.sub(to_remove, " ", sent)
        cleanSent = cleanSent.strip()
        if len(cleanSent) > 0: #if empty string, skipped
            tmp = dict()
            tmp['sent'] = cleanSent
            # for debugging
            '''
            print(cleanSent, end=' ')
            for c in cleanSent:
                print(hex(ord(c)), end=' ')
            print('')
            '''
            # parse the sentence, return an array of typed dependencies
            (tmp['seg_sent'], nodes, edges) = sendConstParseRequest(cleanSent, 
                    returnTokenizedSent=True)
            tmp['nodes'] = nodes
            tmp['edges'] = edges
            result.append(tmp)
    return result

# parse the news
def constParseNews(news):
    news['title_constituent'] = constParseText(news['title'])
    news['content_constituent'] = constParseText(news['content'])
    return news



if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'InNewsJson OutNewsJson Dependency/Constituent', file=sys.stderr)
        exit(-1)
    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]
    parseType = sys.argv[3]
    assert parseType == 'Dependency' or parseType == 'Constituent'

    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)
    
    #random.shuffle(newsDict)
    cnt = 0
    for newsId, news in newsDict.items():
        if parseType == 'Dependency':
            depParseNews(news, draw=True, fileFolder=newsId)
        elif parseType == 'Constituent':
            constParseNews(news)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress: (%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)

    #for reln in allRelationSet:
    #    print(reln)

    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent=1)


