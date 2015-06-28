
import json

# 2015/06/27 for output 7T_Merged

with open('labelFinal.json', 'r') as f:
    labelList = json.load(f)

with open('newsFinalAll_withTopic.json', 'r') as f:
    newsDict = json.load(f)

# find remain news id and its topic
def getRemainLabel(newsDict, nowList):
    newsIdSet = set([label['news_id'] for label in nowList])
    newList = list()
    for newsId, news in newsDict.items():
        if newsId not in newsIdSet:
            label = { 'label': 'agree', 'news_id': newsId, 'statement_id': news['topic'][0] }
            newList.append(label)
    return newList

# reverse statement of topic 2, 6, 13
m = { 'agree': 'oppose', 'oppose': 'agree', 'neutral': 'neutral' }
for label in labelList:
    if label['statement_id'] in [2,6, 13]:
        label['label'] = m[label['label']]

## 2. remove neutral
newList = list()
m = { "agree": "agree", "neutral": "agree", "oppose": "oppose" }
for label in labelList:
    if label['label'] in ['agree', 'oppose']:
        newList.append(label)

print('7T')
with open('labelFinal_7T.json', 'w') as f:
    json.dump(newList, f, indent=2)

remainList = getRemainLabel(newsDict, newList) 
with open('labelFinal_7T_remain.json', 'w') as f:
    json.dump(remainList, f, indent=2)


# 2. merge agree and netral as "not oppose"
newList = list()
m = { "agree": "agree", "neutral": "agree", "oppose": "oppose" }
for label in labelList:
    label['label'] = m[label['label']]
    newList.append(label)

print('7T_merged')
with open('labelFinal_7T_Merged.json', 'w') as f:
    json.dump(newList, f, indent=2)

remainList = getRemainLabel(newsDict, newList) 
with open('labelFinal_7T_Merged_remain.json', 'w') as f:
    json.dump(remainList, f, indent=2)

