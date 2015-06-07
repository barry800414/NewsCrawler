#!/usr/bin/env python3
import sys
import json
import re
import random
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


# parse the news
def tagNews(news, sep=SEP, new_sep=NEW_SEP, to_remove=TO_REMOVE):
    news['title_pos'] = tagText(news['title'], sep, new_sep, to_remove)
    news['content_pos'] = tagText(news['content'], sep, new_sep, to_remove)
    return news

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def tagText(text, sep=SEP, new_sep=NEW_SEP, to_remove=TO_REMOVE, 
        brackets=BRACKETS):
    result = ''
    sentArray = re.split(sep, text)
    
    # for each sentence
    for i, sent in enumerate(sentArray):
        cleanSent = re.sub(to_remove, " ", sent)
        cleanSent = cleanSent.strip()
        if len(cleanSent) > 0: #if empty string, skipped
            tmp = dict()
            tmp['sent'] = cleanSent
            # tag the sentence, return a string with tags
            response = sendTagRequest(cleanSent, seg=False)
            if response == None:
                print('tagging error', file=sys.stderr)
                continue

            # post process
            response = postProcess(response)
            #print('|' + response + '|')

            if len(result) == 0:
                result = response
            else:
                result = result + new_sep + response
    return result

def postProcess(response):
    newStr = ''
    for i, wt in enumerate(response.split(' ')):
        tmp = wt.split('/')
        if len(tmp) != 2:
            print(wt)
            continue
        (w, t) = tmp
        if w.strip() == ',': 
            w = '，'
        else: 
            w = w.replace(',', '')
        if i == 0: 
            newStr = w + '/' + t
        else: 
            newStr = newStr + ' ' + w + '/' + t
    return newStr

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:', sys.argv[0], 'InSegNewsJson OutTaggedNewsJson [PunctuationJson]', file=sys.stderr)
        exit(-1)

    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]

    # read in news file
    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)
    
    # read in punctuation file
    if len(sys.argv) == 4:
        punctuationJsonFile = sys.argv[3]
        punct = Punctuation.readJsonFile(punctuationJsonFile)
        sepRegexStr = Punctuation.toRegexStr(punct['sep'])
        removeRegexStr = Punctuation.toRegexStr(punct['remove'])
    else:
        sepRegexStr = SEP
        removeRegexStr = TO_REMOVE

    cnt = 0
    #tagText("我支持廢除死刑 ,, 但是應該要有終身監禁", sep=sepRegexStr, new_sep=NEW_SEP, to_remove=removeRegexStr)

    for newsId, news in sorted(newsDict.items(), key=lambda x:x[0]):
        tagNews(news, sep=sepRegexStr, new_sep=NEW_SEP, to_remove=removeRegexStr)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress: (%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)
            

    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent = 2)


