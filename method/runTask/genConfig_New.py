

import copy
import json

configFolder = './config/'

# default config of each model
#targetScore = "MacroF1"
targetScore = "Accuracy"
nfolds = 10
testSize = 0.1
defaultConfig={
        "WM": {
            "toRun": ["SelfTrainTest"],
            #"toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": { "method": "binary", "params": { "threshold": 0.0 }},
            "minCnt": 2,
            "params":{ 
                "feature": ["tfidf"],
                "allowedPOS": [["VA", "VV", "NN", "NR", "AD", "JJ"]]
            },
            "setting":{
                "targetScore": targetScore,
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": testSize,
                "n_folds": nfolds,
                "fSelectConfig": None
            },
            "fSelectConfig": None,
            "volc": None,
            "wordGraph": None
        },
        "OLDM_Full": {
            "toRun": ["SelfTrainTest"],
            #"toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": { "method": "binary", "params": { "threshold": 0.0 }},
            "minCnt": 2,
            "params":{ 
                "seedWordType": [
                    {"type": "tag", "allow": ["NR","NN","NP"]}
                ],
                "firstLayerType": [ 
                    {"type": "tag", "allow": ["VV","JJ","VA"]}
                ]
            },
            "setting":{
                "targetScore": targetScore,
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": testSize,
                "n_folds": nfolds,
                "fSelectConfig": None
            },
            "fSelectConfig": None,
            "volc": None,
            "phrase": None,
            "wordGraph": None
        },
        "OLDM_PP": {
            "toRun": ["SelfTrainTest"],
            #"toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": { "method": "binary", "params": { "threshold": 0.0 }},
            "minCnt": 2,
            "params":{ 
                "keyTypeList": [["T"]],
                "opnNameList": [None],
                "negSepList": [[True]],
                "ignoreNeutral": [False]
            },
            "setting":{
                "targetScore": targetScore,
                "targetScore": "Accuracy",
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": testSize,
                "n_folds": nfolds,
                "fSelectConfig": None
            },
            "treePattern": "./DepBased/my_pattern_OLDM.json",
            "volc": None,
            "phrase": None,
            "wordGraph": None
        },
        "OM_noH": {
            "toRun": ["SelfTrainTest"],
            #"toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": { "method": "binary", "params": { "threshold": 0.0 }},
            "minCnt": 2,
            "params":{ 
                "keyTypeList": [["T", "OT"]],
                "opnNameList": [None],
                "negSepList": [[True]],
                "ignoreNeutral": [False]
            },
            "setting":{
                "targetScore": targetScore, 
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": testSize,
                "n_folds": nfolds,
                "fSelectConfig": None
            },
            "treePattern": "./DepBased/my_pattern_noH.json",
            "volc": None,
            "phrase": None,
            "wordGraph": None
        },
        "OM_withH": {
            "toRun": ["SelfTrainTest"],
            #"toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": { "method": "binary", "params": { "threshold": 0.0 }},
            "minCnt": 2,
            "params":{ 
                "keyTypeList": [["H", "T", "HT"]],
                "opnNameList": [None],
                "negSepList": [[True]],
                "ignoreNeutral": [False]
            },
            "setting":{
                "targetScore": targetScore, 
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": testSize,
                "n_folds": nfolds,
                "fSelectConfig": None
            },
            "treePattern": "./DepBased/my_pattern_withH.json",
            "volc": None,
            "phrase": None,
            "wordGraph": None
        }

}

# generate configs for word graph
wgFolder = './WordClustering/wordGraph'
k1 = 20
beta = 0.75
step = 2
topicList = [2, 3, 4, 5, 13, 'All']
wgConfigEachModel = dict()
wgVolcConfig = { 
    "WM": {
        "main": "%s/news7852Final.volc" % (wgFolder) 
    },
    "OLDM_Full": {
        "seed": "%s/news7852Final.volc" % (wgFolder), 
        "firstLayer": "%s/news7852Final.volc" % (wgFolder) 
    },
    "other": {
        "holder":  "%s/news7852Final.volc" % (wgFolder),
        "target": "%s/news7852Final.volc" % (wgFolder),
        "opinion": "%s/news7852Final.volc" % (wgFolder) 
    }
}

for model in ['WM', 'OLDM_Full', 'other']:
    wgConfig = dict()
    if model == 'WM':
        k2Range = [2, 3, 5, 10, 20, 40]
    else:
        k2Range = [2, 3, 5]
    for method in ['TopKEachRow', 'TopK']:
        for k2 in k2Range:
            name = 'wg7852_top%d_beta%d_step%d_%s%d' % (k1, round(beta*100), step, method, k2)
            wgConfig[name] = dict()
            for t in topicList:
                wgConfig[name][t] = { 
                    "filename": "%s/%s.mtx" % (wgFolder, name),
                    "params": {},
                    "volcFile": wgVolcConfig[model]
                }

    name = 'wg7852_top%d_None' % (k1)
    wgConfig[name] = dict()
    for t in topicList:
        wgConfig[name][t] = { 
            "filename": "%s/%s.mtx" % (wgFolder, name),
            "params": {},
            "volcFile": wgVolcConfig[model]
    }

    wgConfigEachModel[model] = wgConfig


# configuration for search parameters (one parameter a time)
iterConfig={
    "WM": [
        { "path": ["preprocess"], 
            "params": {"None": None,
                       "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                       "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },
        #{ "path": ["volc"],
        #    "params": volcFileConfig['WM']
            #}
        #    },
        { "path": ["wordGraph"],
            "params": wgConfigEachModel['WM']
        }
    ],
    "OLDM_Full" :[
        { "path": ["preprocess"], 
            "params": {"None": None,
                       "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                       "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },
        { "path": ["params", "firstLayerType"],
            "params": { "NTUSD": [{"type": "word", "allow": "NTUSD_core"}] }
            },
        #{ "path": ["volc"],
        #    "params": volcFileConfig['OLDM']
        #}  
        { "path": ["wordGraph"],
            "params": wgConfigEachModel['OLDM_Full']
        }
    ],
    "OLDM_PP":[  
        { "path": ["preprocess"], 
            "params": { "None": None,
                        "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                        "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },
        { "path": ["params", "ignoreNeutral"],
            "params": { "iN": [True] }
        },
        #{ "path": ["volc"],
        #    "params": volcFileConfig['OM']
        #},
        { "path": ["wordGraph"],
            "params": wgConfigEachModel['other']
        }
    ],
    "OM_noH":[  
        { "path": ["preprocess"], 
            "params": { "None": None,
                        "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                        "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },
        { "path": ["params", "keyTypeList"], 
            "params": { "T": [["T"]], "OT": [["OT"]] },
            },
        { "path": ["params", "ignoreNeutral"],
            "params": { "iN": [True] }
        },
        #{ "path": ["volc"],
        #    "params": volcFileConfig['OM']
        #},
        { "path": ["wordGraph"],
            "params": wgConfigEachModel['other']
        }
    ],
    "OM_withH":[  
        { "path": ["preprocess"], 
            "params": { "None": None,
                        "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                        "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },
        { "path": ["params", "keyTypeList"], 
            "params": { "T": [["T"]], "H": [["H"]], "HT":[["HT"]], "HOT": [["HOT"]], 
                "OT": [["OT"]], "HO":[["HO"]], "all": [["H", "T", "OT", "HO", "HOT", "HT"]],
                "Tall": [["OT", "T"]], "Hall": [["HO", "H"]] },
            },
        { "path": ["params", "ignoreNeutral"],
            "params": { "iN": [True] }
        },
        #{ "path": ["volc"],
        #    "params": volcFileConfig['OM']
        #},
        { "path": ["wordGraph"],
            "params": wgConfigEachModel['other']
        }
    ]

}

nameList= {
    "WM": [ "binary", "N"], #pre, wg
    "OLDM_Full":  ["binary", "Tag", "N"], #pre, feature, wg
    "OLDM_PP": [ "binary", "igFalse", "N" ], #pre, ignore, wg
    "OM_noH": [ "binary", "Tall", "igFalse", "N"], #pre, keyType, ignore, wg
    "OM_withH": [ "binary", "H-T-HT", "igFalse", "N"] # pre, keyType, ignore, wg
    #"OM_noH": [ "binary", "igFalse", "Tall", "N"], #pre, keyType, ignore, wg
    #"OM_withH": [ "binary", "igFalse", "H-T-HT", "N"] # pre, keyType, ignore, wg

}


def genConfig(defaultConfig, iterConfig, nameList, prefix):
    configList = list()
    for i in range(0, len(iterConfig)):
        path = iterConfig[i]["path"]
        params = iterConfig[i]["params"]
        for pName, p in sorted(params.items()):
            newConfig = copy.deepcopy(defaultConfig)
            newNameList = copy.deepcopy(nameList)
            
            # replace new configs
            obj = newConfig
            for j in range(0, len(path) - 1):
                obj = obj[path[j]]
            obj[path[-1]] = p
            newNameList[i] = pName
            newName = mergeName(prefix, newNameList)
            newConfig['taskName'] = newName
            configList.append( (newName, newConfig) )
    return configList


def genSingleConfig(defaultConfig, iterConfig, nameList, prefix, modelName, selectedList):
    assert len(nameList) == len(selectedList)
    newConfig = copy.deepcopy(defaultConfig[modelName])
    newNameList = copy.deepcopy(nameList)

    for i in range(0, len(selectedList)):
        pName = selectedList[i] 
        if pName is None:
            # keep default config
            continue
        path = iterConfig[i]['path']
        paramsDict = iterConfig[i]['params']
        if pName in paramsDict:
            obj = newConfig
            for j in range(0, len(path) - 1):
                obj = obj[path[j]]
            obj[path[-1]] = paramsDict[name]
            newNameList[i] = pName
        else:
            print(name, ' not found !', file=sys.stderr)

    newName = mergeName(prefix, newNameList)
    newConfig['taskName'] = newName
    return (newName, newConfig)


def mergeName(prefix, nameList):
    outStr = str(prefix)
    for n in nameList:
        outStr += '_' + n
    return outStr

if __name__ == '__main__':
    suffix = '_TwoClass'
    suffix = '_5T_Merged'
    #suffix = '_4T'
    #suffix = '_Filtered_5T_Merged'

    # for single model
    for model in ["WM", "OLDM_Full", "OLDM_PP", "OM_noH", "OM_withH"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model + suffix)
        print(model, len(configList))
        for name, config in configList:
            with open(configFolder + name + '_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print(name)
            #print(config, '\n')
            pass
    
    suffix = '_4T'
    # for merged model
    # WM+OLDM, WM+OM, WM is fixed
    for model in ["OLDM_PP", "OM_withH"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = 'WM_' + model + suffix)
        print("WM_"+ model, len(configList))
        for name, config in configList:
            #with open(configFolder + name + '_config.json', 'w') as f:
            #    json.dump(config, f, indent=2)
            #print(name)
            #print(config)
            pass

    # WM and OLDM is fixed
    for model in ["OM_withH"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = 'WM_OLDM_PP_' + model + suffix)
        print("WM_OLDM_"+ model, len(configList))
        for name, config in configList:
            #with open(configFolder + name + '_config.json', 'w') as f:
            #    json.dump(config, f, indent=2)
            #print(name)
            #print(config)
            pass

# generating configs for word clustering 
volcFolder = './WordClustering/volc'
volcFileConfig = { "WM": dict(), "OLDM": dict(), "OM": dict() }

# for WM
c = volcFileConfig['WM']
#for type in ["c7852", "c7852_Gov"]:
for type in ["c7852"]:
    c[type] = dict()
    for t in topicList:
        c[type][t] = dict()
        c[type][t]['main'] = '%s/WM_%s_T%s.volc' % (volcFolder, type, str(t))

# for OLDM
c = volcFileConfig['OLDM']
#for type in ['c7852_NTUSD', 'c7852_Tag', 'c7852_NTUSD_Gov', 'c7852_Tag_Gov']:
for type in ['c7852_NTUSD', 'c7852_Tag']:
    c[type] = dict()
    for t in topicList:
        c[type][t] = dict()
        c[type][t]['seed'] = '%s/OLDM_%s_T%s_sW.volc' % (volcFolder, type, str(t))
        c[type][t]['firstLayer'] = '%s/OLDM_%s_T%s_flW.volc' % (volcFolder, type, str(t))
# for OM
c = volcFileConfig['OM']
#for type in ['c7852', 'c7852_Gov']:
for type in ['c7852']:
    c[type] = dict()
    for t in topicList:
        c[type][t] = dict()
        c[type][t]['holder'] = '%s/OM_%s_T%s_hdW.volc' % (volcFolder, type, str(t))
        c[type][t]['opinion'] = '%s/OM_%s_T%s_opnW.volc' % (volcFolder, type, str(t))
        c[type][t]['target'] = '%s/OM_%s_T%s_tgW.volc' % (volcFolder, type, str(t))
#print(volcFileConfig)

