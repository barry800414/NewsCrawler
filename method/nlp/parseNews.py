#!/usr/bin/env python3
import sys
import json
import re
from NLPToolRequests import *
import Punctuation

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
def depParseNews(news, draw=False, fileFolder=None, sep=SEP, 
        new_sep=NEW_SEP, to_remove=TO_REMOVE):
    news['title_dep'] = depParseText(news['title'], draw=draw, 
            fileFolder=fileFolder, fileName='title', sep=sep,
            new_sep=new_sep, to_remove=to_remove)
    news['content_dep'] = depParseText(news['content'], draw=draw, 
            fileFolder=fileFolder, fileName='content', sep=sep,
            new_sep=new_sep, to_remove=to_remove)
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
def constParseNews(news, sep=SEP, new_sep=NEW_SEP, to_remove=TO_REMOVE) :
    news['title_constituent'] = constParseText(news['title'], sep=sep,
            new_sep=new_sep, to_remove=to_remove)
    news['content_constituent'] = constParseText(news['content'], sep=sep,
            new_sep=new_sep, to_remove=to_remove)
    return news


if __name__ == '__main__':
    if len(sys.argv) < 4:
        print('Usage:', sys.argv[0], 'InNewsJson OutNewsJson Dependency/Constituent PunctuationJson', file=sys.stderr)
        exit(-1)
    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]
    parseType = sys.argv[3]
    assert parseType == 'Dependency' or parseType == 'Constituent'

    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)
    
    # read in punctuation file
    if len(sys.argv) == 5:
        punctuationJsonFile = sys.argv[4]
        punct = Punctuation.readJsonFile(punctuationJsonFile)
        sepRegexStr = Punctuation.toRegexStr(punct['sep'])
        removeRegexStr = Punctuation.toRegexStr(punct['remove'])
    else:
        sepRegexStr = SEP
        removeRegexStr = TO_REMOVE

    cnt = 0
    for newsId, news in newsDict.items():
        if parseType == 'Dependency':
            depParseNews(news, draw=True, fileFolder=newsId, 
                    sep=sepRegexStr, new_sep=NEW_SEP, 
                    to_remove=removeRegexStr)
        elif parseType == 'Constituent':
            constParseNews(news, sep=sepRegexStr, new_sep=NEW_SEP, 
                    to_remove=removeRegexStr)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress: (%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)

    #for reln in allRelationSet:
    #    print(reln)

    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent=1)


