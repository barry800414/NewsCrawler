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
def constParseEngNews(news, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP):
    news['content_constituent'] = constParseEngText(news['content'], sepSet, rmFirstSet, rmLaterSet, new_sep=new_sep)
    return news

def constParseEngText(text, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP):
    result = list()
    #print('\033[1;33moriginal:\033[0m|' + text + '|')
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
        response = sendConstParseRequest(sent, seg=True)
        if response == None:
            print('Parsing error', file=sys.stderr)
            continue
        (nodes, edges) = response
        #print(nodes)
        #print(edges)

        if len(nodes) != 0 and len(edges) != 0:
            result.append({'nodes': nodes, 'edges': edges})

    #print('\033[0;32mTagging Result:\033[0m|' + result + '|\n')
    return result

# parse the news
def depParseEngNews(news, sepSet, rmFirstSet, rmLaterSet, 
        new_sep=NEW_SEP, draw=False, fileFolder=None, fileName=''):
    news['content_dep'] = depParseEngText(news['content'], sepSet, 
            rmFirstSet, rmLaterSet, new_sep=new_sep, draw=draw, 
            fileFolder=fileFolder, fileName='content')
    return news

def depParseEngText(text, sepSet, rmFirstSet, rmLaterSet, 
        new_sep=NEW_SEP, draw=False, fileFolder=None, fileName=''):
    result = list()
    #print('\033[1;33moriginal:\033[0m|' + text + '|')
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
        response = sendDepParseRequest(sent, seg=True, draw=draw, 
                fileFolder=fileFolder, fileName=fileName+"_%04d_%s" %(
                    i,sent))
        if response == None:
            print('Parsing error', file=sys.stderr)
            continue
        #print(response)
        #print(edges)

        if len(response) != 0:
            result.append({'tdList': response})

    #print('\033[0;32mTagging Result:\033[0m|' + result + '|\n')
    return result



# parse the news
def parseEngNews(news, sepSet, rmFirstSet, rmLaterSet, 
        new_sep=NEW_SEP, draw=False, fileFolder=None, fileName=''):
    (news['content_constituent'], news['content_dep']) = parseEngText(
            news['content'], sepSet, rmFirstSet, rmLaterSet, 
            new_sep=new_sep, draw=draw, fileFolder=fileFolder, 
            fileName='content')
    return news


def parseEngText(text, sepSet, rmFirstSet, rmLaterSet, 
        new_sep=NEW_SEP, draw=False, fileFolder=None, fileName=''):
    constResult = list()
    depResult = list()
    
    #print('\033[1;33moriginal:\033[0m|' + text + '|')
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
        response = sendParseRequest(sent, seg=True, draw=draw, 
                fileFolder=fileFolder, fileName=fileName+"_%04d_%s" %(
                    i,sent))
        if response == None:
            print('Parsing error', file=sys.stderr)
            continue
        
        (constR, depR) = response
        #print('ConstR:', constR)
        #print('depR:', depR)
        constResult.append({'nodes': constR[0], 'edges': constR[1]})
        depResult.append({'tdList': response})

    #print('\033[0;32mTagging Result:\033[0m|' + result + '|\n')
    return (constResult, depResult)



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
    if len(sys.argv) != 5:
        print('Usage:', sys.argv[0], 'InSegNewsJson OutTaggedNewsJson PunctuationJson Dep/Const/Dep_Const', file=sys.stderr)
        exit(-1)

    inNewsJsonFile = sys.argv[1]
    outNewsJsonFile = sys.argv[2]
    punctuationJsonFile = sys.argv[3]
    parseType = sys.argv[4]
    assert parseType == 'Dep' or parseType == 'Const' or parseType == 'Dep_Const'

    # read in news file
    with open(inNewsJsonFile, 'r') as f:
        newsDict = json.load(f)
    
    # read in punctuation file
    punct = Punctuation.readJsonFile(punctuationJsonFile)
    sepSet= set(punct['sep'].keys())
    rmFirstSet = set(punct['remove_first'].keys())
    rmLaterSet = set(punct['remove_later'].keys())

    cnt = 0
    for newsId, news in sorted(newsDict.items(), key=lambda x:x[0]):
        if parseType == 'Dep':
            depParseEngNews(news, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP, draw=True, fileFolder=newsId)
        elif parseType == 'Const':
            constParseEngNews(news, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP)
        elif parseType == 'Dep_Const':
            parseEngNews(news, sepSet, rmFirstSet, rmLaterSet, new_sep=NEW_SEP, draw=True, fileFolder=newsId)
        cnt += 1
        if cnt % 10 == 0:
            print('Progress: (%d/%d)' % (cnt, len(newsDict)), file=sys.stderr)
            
    with open(outNewsJsonFile, 'w') as f:
        json.dump(newsDict, f, ensure_ascii=False, indent = 2)


