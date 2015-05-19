
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

# paramsDict: a dict (name of model -> a list of parameters)
def getParamsIter(paramsDict, framework, topicId=None, newList=list(), goneSet=set(), finalP=dict()):
    toGo = set(paramsDict.keys()) - goneSet
    if len(toGo) == 0:
        newList.append(dict(finalP))
    else:
        name = sorted(list(toGo))[0]
        goneSet.add(name)
        if topicId != None:
            pList = paramsDict[name][framework][topicId]
        else:
            pList = paramsDict[name][framework]
        for p in pList:
            finalP[name] = p
            getParamsIter(paramsDict, framework, topicId, newList, goneSet, finalP)
            del finalP[name]
        goneSet.remove(name)
        return newList

'''
def getParamsIter(pList1, p1Name, pList2, p2Name):
    newList = list()
    for p1 in pList1:
        for p2 in pList2:
            newList.append( { p1Name: p1, p2Name:p2 } )
    return newList
'''

if __name__ == '__main__':
    # test case
    paramsDict = {
        "WM": [
                {"allowedPOS": ["NN", "NT"]},
                {"allowedPOS": ["NN", "NR"]}
            ],
        "OLDM": [
                {"firstLayer": ["VA", "VV"]},
                {"firstLayer": ["AD", "JJ"]}
            ],
        "OM": [
                {"keyTypeList": [["H", "T", "HT"]]},
                {"keyTypeList": [["HOT", "OT", "HO"]]}
            ]
    }

    paramsIter = getParamsIter(paramsDict)

    for p in paramsIter:
        print(p)

