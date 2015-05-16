#!/usr/bin/env python3
import sys
import json
import re
import random
import nltk
from NLPToolRequests import *
import Punctuation 


# default new sentence separator
NEW_SEP = ','

# parse the news
def tagEngNews(news, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP):
    news['content_pos'] = tagEngText(news['content'], sepSet, rmFirstSet, rmLaterSet, new_sep=new_sep)
    return news

# segment all the sentences, dealing with punctuations
# sep: the sentence separators of original contents(for regex)
# new_sep: the new sentence separator
# brackets: the brackets. the content in brackets will not be segemented
def tagEngText(text, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP):
    result = ''
    print('\033[1;33moriginal:\033[0m|' + text + '|')
    # remove some punctuation first
    rmFirstRegex = Punctuation.set2RegexStr(rmFirstSet)
    cleanText = re.sub(rmFirstRegex, " ", text)
    cleanText = cleanText.strip()
    #print('CleanedSent:|' + cleanText + '|')
    sentList = splitSent(cleanText, sepSet)
    
    # for each sentence
    for i, sent in enumerate(sentList):
        #print('|' + sent + '|')
        # tag the sentence, return a string with tags
        response = sendTagRequest(sent, seg=True)
        if response == None:
            print('Tagging error', file=sys.stderr)
            continue

        # remove original sentence separator
        response = removeSepStr(response, rmLaterSet)
        #print('\tTagged:|' + response + '|')
        if len(result) == 0:
            result = response
        else:
            result = result + new_sep + response
    print('\033[0;32mTagging Result:\033[0m|' + result + '|\n')
    return result

def removeSepStr(string, sepSet):
    outStr = ''
    entry = string.strip().split(' ')
    for e in entry:
        (w, t) = e.split('/')
        if w not in sepSet:
            if len(outStr) == 0:
                outStr = str(e)
            else:
                outStr = outStr + ' ' + e
    return outStr


def splitSent(text, sepSet):
    tokens = nltk.word_tokenize(text)
    sentList = list()
    sent = ''
    for i, t in enumerate(tokens):
        if t in sepSet and len(sent) != 0:
            sentList.append(sent)
            sent = ''
        else:
            if len(sent) == 0:
                sent = str(t)
            else:
                sent = sent + ' ' + t
    return sentList
        

def mergeTokens(tokens):
    outStr = ''
    for i, t in enumerate(tokens):
        if i == 0:
            outStr = str(t)
        else:
            outStr = outStr + ' ' + t
    return outStr


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('Usage:', sys.argv[0], 'InSegNewsJson OutTaggedNewsJson PunctuationJson', file=sys.stderr)
        exit(-1)

    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]

    # read in news file
    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)
    
    # read in punctuation file
    punctuationJsonFile = sys.argv[3]
    punct = Punctuation.readJsonFile(punctuationJsonFile)
    sepSet= set(punct['sep'].keys())
    rmFirstSet = set(punct['remove_first'].keys())
    rmLaterSet = set(punct['remove_later'].keys())

    cnt = 0
    for newsId, news in sorted(newsDict.items(), key=lambda x:x[0]):
        tagEngNews(news, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress: (%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)
            
    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent = 2)


