
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
    return __getParamsIter(paramsDict, framework, topicId, list(), set(), dict())

def __getParamsIter(paramsDict, framework, topicId=None, newList=list(), goneSet=set(), finalP=dict()):
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
            __getParamsIter(paramsDict, framework, topicId, newList, goneSet, finalP)
            del finalP[name]
        goneSet.remove(name)
        return newList



if __name__ == '__main__':
    # test case 1
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
    #paramsIter = getParamsIter(paramsDict)
    #for p in paramsIter:
    #    print(p)

    WMParams = loadFrameworkTopicParams("WM_cluster7852_300_params.json")
    OLDMParams = loadFrameworkTopicParams("OLDM_cluster7852_300_params.json")
    #print(json.dumps(WMParams, indent=2))
    #print(json.dumps(OLDMParams, indent=2))

    paramsDict = dict()
    paramsDict['WM'] = WMParams
    paramsDict['OLDM'] = OLDMParams

    for t in [2, 3, 4, 5, 6, 13, 16]:
        paramsIter = getParamsIter(paramsDict, framework="SelfTrainTest", topicId=t)
        print('Topic %d: %d' % (t, len(paramsIter)))
        print('---------------------------------------------')
