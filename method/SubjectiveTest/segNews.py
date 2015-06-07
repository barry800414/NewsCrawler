#!/usr/bin/env python3
import sys
import json
import re

from NLPToolRequests import *
import Punctuation

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
def segLabelNews(newsDict, sep=SEP, new_sep=NEW_SEP, to_remove=TO_REMOVE):
    newsDict['title_seg'] = segText(newsDict['title'], sep, new_sep, to_remove)
    newsDict['content_seg'] = segText(newsDict['content'], sep, new_sep, to_remove)
    return newsDict

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def segText(content, sep=SEP, new_sep=NEW_SEP, 
        to_remove=TO_REMOVE, brackets=BRACKETS):
    result = ''
    sArray = re.split(sep, content)
    for sent in sArray:
        cleanSent = re.sub(to_remove, " ", sent)
        cleanSent = cleanSent.strip()
        if len(cleanSent) == 0: #if empty string, skip it
            continue
        
        #print('|%s|' % (s2))
        # segment the string by Stanford NLP segmenter
        response = sendSegmentRequest(cleanSent)
        # normalizing spaces (N -> 1 space char)
        response = re.sub('[ ]+', ' ', response)
        # remove delimeter chars in front/end of string
        response = response.strip()
        #print('|%s|' % result)
        
        if len(response) == 0:
            continue
        if len(result) != 0:
            result += NEW_SEP + reponse
        else:
            result += reponse
    return result

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:', sys.argv[0], 'InNewsJson OutNewsJson [PunctuationJson]', file=sys.stderr)
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
    for newsId, news in sorted(newsDict.items()):
        segLabelNews(news, sep=sepRegexStr, new_sep=NEW_SEP, to_remove=removeRegexStr)
        cnt += 1
        if (cnt+1) % 10 == 0:
            print('%cProgress: (%d/%d)' % (13, cnt+1, len(newsDict)), end='', file=sys.stderr)

    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent = 2)


