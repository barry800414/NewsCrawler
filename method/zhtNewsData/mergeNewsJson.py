
import json
#fileList = ['news.json', 'segNews.json', 'taggedNews.json', 'constParsedNews.json', 'depParsedNews.json']
#contentCol = ['content', 'content_seg', 'content_pos', 'content_const', 'content_dep']
#titleCol = ['title', 'title_seg', 'title_pos', 'title_const', 'title_dep']

fileList = ['taggedNews20150419_new.json', 'depParsedNews20150419_new.json']
contentCol = ['content_pos', 'content_dep']
titleCol = ['title_pos', 'title_dep']
outFile = 'taggedAndDepParsedNews20150419_new.json'

newsJsonList = list()
for file in fileList:
    with open(file, 'r') as f:
        newsJsonList.append(json.load(f))

newsIdSet = set(newsJsonList[0].keys())
for i in range(1, len(newsJsonList)):
    newsIdSet2 = set(newsJsonList[i].keys())
    if newsIdSet != newsIdSet2:
        print('news are different', file=sys.stderr)
        exit(-1)

finalJson = { newsId: dict() for newsId in newsIdSet }
for i, newsJson in enumerate(newsJsonList):
    for newsId in newsIdSet:
        finalJson[newsId][contentCol[i]] = newsJson[newsId][contentCol[i]]
        finalJson[newsId][titleCol[i]] = newsJson[newsId][titleCol[i]]

for newsId in newsIdSet:
    finalJson[newsId]['topic'] = newsJsonList[0][newsId]['topic']


with open(outFile, 'w') as f:
    json.dump(finalJson, f, ensure_ascii=False, indent=2)
