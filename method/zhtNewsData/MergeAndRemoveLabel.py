
import json

# 2015/06/22

with open('labelFinal.json', 'r') as f:
    labelList = json.load(f)

# reverse statement of topic 2 and 13
m = { 'agree': 'oppose', 'oppose': 'agree', 'neutral': 'neutral' }
for label in labelList:
    if label['statement_id'] in [2, 13]:
        label['label'] = m[label['label']]

# 1. remove topic 3 topics (topic2, 6, 16) 
newList = list()
for label in labelList:
    if label['statement_id'] in [3, 4, 5, 13]:
        newList.append(label)

stat = { t:{ 'agree': 0, 'neutral': 0, 'oppose':0 } for t in [3, 4, 5, 13] }
for label in newList:
    t = label['statement_id']
    l = label['label']
    stat[t][l] += 1
print('4T')
for t, cnt in stat.items():
    print(t, cnt)

with open('labelFinal_4T.json', 'w') as f:
    json.dump(newList, f, indent=2)


# 2. merge agree and netral as "not oppose", remove topic 6, 16
newList = list()
m = { "agree": "agree", "neutral": "agree", "oppose": "oppose" }
for label in labelList:
    if label['statement_id'] in [2, 3, 4, 5, 13]:
        label['label'] = m[label['label']]
        newList.append(label)

stat ={ t:{ 'agree': 0, 'neutral': 0, 'oppose':0 } for t in [2, 3, 4, 5, 13] }
for label in newList:
    t = label['statement_id']
    l = label['label']
    stat[t][l] += 1
print('5T_merged')
for t, cnt in stat.items():
    print(t, cnt)

with open('labelFinal_5T_Merged.json', 'w') as f:
    json.dump(newList, f, indent=2)


