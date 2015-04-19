
import sys
import json
from sentiDictSum import readSentiDict
from colorText import *

if __name__ == '__main__':
    if len(sys.argv)!= 4:
        print('Usage:', sys.argv[0], 'labelNewsJsonFile wordLexicon targetLexicon', file=sys.stderr)
        exit(-1)
    
    labelNewsJsonFile = sys.argv[1]
    wordLexiconFile = sys.argv[2]
    targetLexiconFile = sys.argv[3]

    # load label news
    with open(labelNewsJsonFile, 'r') as f:
        labelNewsList = json.load(f)
    
    # load sentiment lexicon & generate word -> color mapping (for sentiment lexicon)
    sentiDict = readSentiDict(wordLexiconFile)
    wordColorForSent = dictToWordColorMapping(sentiDict)

    '''
    # load opinion targets list for each topic
    with open(targetLexiconFile, 'r') as f:
        targetLexiconJson = json.load(f)
    targetLexicon = { topic['id']: topic['keywords'] for topic in targetLexiconJson }

    # generate word -> color mapping for each topic
    wordColor = dict()
    for topicID, wordList in targetLexicon.items():
        wordColor[topicID] = wordColorForSent.copy()
        for w in wordList:
            if w in wordColor[topicID]:
                print('%s overlapping!' % (w), file=sys.stderr)
            wordColor[topicID][w] = WC.YELLOW

    print('Coloring contents ... ', file=sys.stderr)
    for i, labelNews in enumerate(labelNewsList):
        statID = labelNews['statement_id']
        label = labelNews['label']
        stat = labelNews['statement']
        title = labelNews['news']['title']
        content = labelNews['news']['content']
        
        print(ct2("立場:", WC.LIGHT_BLUE), ct(stat, wordColor[statID]))
        print(ct2("標記:", WC.LIGHT_BLUE), label)
        print(ct2("標題:", WC.LIGHT_BLUE), ct(title, wordColor[statID]))
        print(ct2("內文:", WC.LIGHT_BLUE), ct(content, wordColor[statID]))
        print('=================================================================')

        if i % 10 == 0:
            print('Progress:(%d/%d)' % (i, len(labelNewsList)), file=sys.stderr)
    '''
    for i, labelNews in enumerate(labelNewsList):
        statID = labelNews['statement_id']
        label = labelNews['label']
        stat = labelNews['statement']['seg']
        title = labelNews['news']['title_seg']
        content = labelNews['news']['content_seg']
        
        print(ct2("立場:", WC.LIGHT_BLUE), ct(stat, wordColorForSent))
        print(ct2("標記:", WC.LIGHT_BLUE), label)
        print(ct2("標題:", WC.LIGHT_BLUE), ct(title, wordColorForSent))
        print(ct2("內文:", WC.LIGHT_BLUE), ct(content, wordColorForSent))
        print('=================================================================')

        if i % 10 == 0:
            print('Progress:(%d/%d)' % (i, len(labelNewsList)), file=sys.stderr)

