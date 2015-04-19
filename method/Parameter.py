
import json

# load parameters json file
# fTopicParams[f][t] is a list of parameters under f framework and topic t
def loadFrameworkTopicParams(filename):
    with open(filename, 'r') as f:
        fTopicParams = json.load(f)
    for framework, topicParams in fTopicParams.items():   
        if type(topicParams) == dict:
            topicSet = set(topicParams.keys())
            for topicId in topicSet:
                topicParams[int(topicId)] = topicParams.pop(topicId)
    return fTopicParams

def getParamsIter(pList1, p1Name, pList2, p2Name):
    newList = list()
    for p1 in pList1:
        for p2 in pList2:
            newList.append( { p1Name: p1, p2Name:p2 } )
    return newList
