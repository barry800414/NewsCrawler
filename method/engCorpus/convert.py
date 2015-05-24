#!/usr/bin/env python3 
import os 
import codecs
import json

DATA_FOLDER='./data'
FILE_ENCODING='latin'

# convert the content of debate to labelNews format
def convert(filename, newsId, statId, stat):
    label = dict()
    news = dict()
    label['statement'] = stat
    label['statement_id'] = statId

    # just assume stance1 => agree, stance2 => oppose
    mapping = {"stance1": "agree", "stance2": "oppose"}

    hasLabel = False
    hasContent = False
    with codecs.open(filename, 'r', encoding=FILE_ENCODING) as f:
        for i, line in enumerate(f):
            if i == 0: #stance
                stance = line.split('=')[1].strip()
                label['label'] = mapping[stance]
                hasLabel = True
            elif i == 1: # original stance text
                continue
            elif i == 2: # original topic
                continue 
            elif i == 3: # content
                label['news_id'] = newsId
                news['content'] = line.strip()
                news['topic'] = [statId]
                hasContent = True
    if hasLabel and hasContent:
        return (label, news)
    else:
        print('File format error:', filename, file=sys.stderr)
    
'''
statMap = { "abortion" : "Women have rights to abortion",
            "creation" : ""}
'''

statDict = dict()
labelList = list()
newsDict = dict()
statId = 1 


for dirpath, dirnames, filenames in os.walk(DATA_FOLDER):
    if dirpath == DATA_FOLDER:
        continue
    agreeNum = 0
    opposeNum = 0
    stat = dirpath.split('/')[-1]
    statDict[statId] = { "original" : stat } 
    fileNum = len(filenames)
    for i in range(0, fileNum):
        filePath = dirpath + '/post_%d' % (i) 
        newsId = "%s_%04d" %(stat, i)
        (label, news) = convert(filePath, newsId, statId, stat)
        if label['label'] == 'agree':
            agreeNum += 1
        elif label['label'] == 'oppose':
            opposeNum += 1
        news['title'] = ''
        labelList.append(label)
        newsDict[newsId] = news
    print('dirPath:', dirpath, '#total:', fileNum, '#Agree:', agreeNum, '#oppose:', opposeNum)
    statId += 1

#with open('engLabel.json', 'w') as f:
#    json.dump(labelList, f, ensure_ascii=False, indent=2)

#with open('engNews.json', 'w') as f:
#    json.dump(newsDict, f, ensure_ascii=False, indent=2)

#with open('engStat.json', 'w') as f:
#    json.dump(statDict, f, ensure_ascii=False, indent=2)

    

