
import sys
import json
import codecs

from NewsLoader import NewsLoader

# get news from label json file
# 2015/06/02

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print >>sys.stderr, 'Usage:', sys.argv[0], 'dbInfoJson InLabelJson OutNewsJson'
        exit(-1)

    dbInfoJsonFile = sys.argv[1]
    inLabelJsonFile = sys.argv[2]
    outNewsJsonFile = sys.argv[3]

    with open(dbInfoJsonFile, 'r') as f:
        dbInfo = json.load(f)
    with open(inLabelJsonFile, 'r') as f:
        labels = json.load(f)

    nl = NewsLoader(dbInfo)
    
    newsIdSet = set()
    for label in labels:
        newsIdSet.add(label['news_id'])

    newsDict = dict()
    for newsId in newsIdSet:
        news = nl.getNews(newsId, 'merge_necessary_clean')
        newsDict[newsId] = news
    
    print '#news:', len(newsDict) 

    with codecs.open(outNewsJsonFile, 'w', encoding='utf-8') as f:
        json.dump(newsDict, f, indent=2 , ensure_ascii=False, sort_keys=True)


    '''
    keyList = sorted(newsDict.keys())
    num = [356, 350, 350, 120, 120, 120, 120]

    nowIndex = 0
    for i, n in enumerate(num):
        partDict = dict()
        for j in range(0, n):
            partDict[keyList[nowIndex]] = newsDict[keyList[nowIndex]]
            nowIndex += 1
        print len(partDict)

        with codecs.open(outNewsJsonFile + '_part%d.txt' % (i), 'w', encoding='utf-8') as f:
            json.dump(partDict, f, indent=2, ensure_ascii=False, sort_keys=True)
    '''
