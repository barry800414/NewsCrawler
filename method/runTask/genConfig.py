

import copy
import json

configFolder = './config/'

# default config of each model
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
                #"targetScore": "MacroF1",
                "targetScore": "Accuracy",
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": 0.2,
                "n_folds": 3,
                "fSelectConfig": None
            },
            "fSelectConfig": None,
            "volc": None,
            "wordGraph": None
        },
        "OLDM": {
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
                #"targetScore": "MacroF1",
                "targetScore": "Accuracy",
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": 0.2,
                "n_folds": 3,
                "fSelectConfig": None
            },
            "fSelectConfig": None,
            "volc": None,
            "phrase": None,
        },
        "OM": {
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
                #"targetScore": "MacroF1",
                "targetScore": "Accuracy",
                "clfName": "MaxEnt",
                "randSeedList": [i for i in range(1,31)],
                "testSize": 0.2,
                "n_folds": 3,
                "fSelectConfig": None
            },
            "treePattern": "./DepBased/my_pattern.json",
            "volc": None,
            "phrase": None,
        },
}


# generating configs for word clustering 
volcFolder = './WordClustering/volc'
topicList = [2, 3, 4, 5, 13, 'All']
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

# generate configs for word graph
wgFolder = './WordClustering/wordGraph'
wgConfig = dict()
for topK in [5, 10, 20]:
    for beta in [0.25, 0.5, 0.75]:
        for step in [10]:
            for selectTopK in [5, 10, 20]:
                name = 'Top%d-beta%d-step%d-select%d' % (topK, int(beta * 100), step, selectTopK)
                wgConfig[name] = dict()
                for t in topicList:
                    wgConfig[name][t] = { 
                            "filename": "%s/wg7852_top%s.mtx" % (wgFolder, topK),
                            "volcFile": { "main": "%s/news7852Final.volc" % (wgFolder) },
                            "params": {
                                "beta": beta,
                                "step": step,
                                "method": "TopK",
                                "value": selectTopK
                            }
                        }
#for k, v in wgConfig.items():
#    print(k, v)

# configuration for search parameters (one parameter a time)
iterConfig={
    "WM": [
        { "path": ["preprocess"], 
            "params": {"None": None,
                       "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                       "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },

        { "path": ["setting", "clfName"], 
            "params": { "RF": "RF" }
            },
        
        { "path": ["params", "feature"], 
            "params": { "01": ["0/1"], } 
            },
        { "path": ["volc"],
            "params": volcFileConfig['WM']
            #}
            },
        { "path": ["wordGraph"],
            "params": wgConfig,
        }
    ],
    "OLDM" :[
        { "path": ["preprocess"], 
            "params": {"None": None,
                       "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                       "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },

        { "path": ["setting", "clfName"], 
            "params": { "RF": "RF" }
            },
            
        { "path": ["params", "firstLayerType"],
            "params": { "NTUSD": [{"type": "word", "allow": "NTUSD_core"}] }
            },
        { "path": ["volc"],
            "params": volcFileConfig['OLDM']
        }

    ],
    "OM":[  
        { "path": ["preprocess"], 
            "params": { "None": None,
                        "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                        "minmax": { "method": "minmax", "params": { "feature_range": [0,1] }}
                       }
            },

        { "path": ["setting", "clfName"], 
            "params": { "RF": "RF" }
            },

        { "path": ["params", "keyTypeList"], 
            "params": { "T": [["T"]], "H": [["H"]], "HT":[["HT"]], "HOT": [["HOT"]], 
                "OT": [["OT"]], "HO":[["HO"]], "all": [["H", "T", "OT", "HO", "HOT", "HT"]]}
            },
        
        { "path": ["params", "ignoreNeutral"],
            "params": { "iN": [True] }
        },

        { "path": ["volc"],
            "params": volcFileConfig['OM']
        },

        { "path": ["treePattern"],
            "params": { "OLDM": "./DepBased/my_pattern_OLDM.json" }
        }
    ]
}

nameList= {
    "WM": [ "binary", "MaxEnt", "tfidf", "N", "N"], #pre, clf, feature, volc, wg
    "OLDM":  [ "binary", "MaxEnt", "Tag", "N"], #pre, clf, feature, volc
    "OM": [ "binary", "MaxEnt", "H-T-HT", "N", "N", "v1"] # pre, clf, feature, neg, ignoreNeutral, volc, patternFile
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
    for model in ["WM", "OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model + suffix)
        print(model, len(configList))
        for name, config in configList:
            with open(configFolder + name + '_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print(name)
            #print(config, '\n')
            pass
    
    suffix = '_5T_Merged_withWG'
    # for merged model
    # WM+OLDM, WM+OM, WM is fixed
    for model in ["OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = 'WM_' + model + suffix)
        print("WM_"+ model, len(configList))
        for name, config in configList:
            with open(configFolder + name + '_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print(name)
            #print(config)
            pass

    # WM and OLDM is fixed
    for model in ["OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = 'WM_OLDM_' + model + suffix)
        print("WM_OLDM_"+ model, len(configList))
        for name, config in configList:
            with open(configFolder + name + '_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print(name)
            #print(config)
            pass



if __name__ == '__main2__':
    cnt = 0
    # generate config first
    for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
        for pre in [None, 'std', 'norm1', 'norm2', 'binary']:
            c = copy.deepcopy(template[model])
            p = c['preprocess']
            prefix = '%s_%s_None' % (model, pre)
            if pre == 'std':
                p['method'] = 'std'
                p['params'] = dict()
                p['params']['with_mean'] = False
                p['params']['with_std'] = True
                c['taskName'] = prefix
            elif pre == 'norm1':
                p['method'] = 'norm'
                p['params'] = dict()
                p['params']['norm'] = 'l1'
                c['taskName'] = prefix
            elif pre == 'norm2':
                p['method'] = 'norm'
                p['params'] = dict()
                p['params']['norm'] = 'l2'
                c['taskName'] = prefix
            elif pre == 'binary':
                if model == 'WM':
                    c['params']['feature'] = ['tf']
                if model == 'OM':
                    c['params']['negSepList'] = [[True]]
                p['method'] = 'binary'
                p['params'] = dict()
                p['params']['threshold'] = 0.0
                c['taskName'] = prefix
            elif pre == None:
                c['preprocess'] = None
                c['taskName'] = prefix
            c['setting']['fSelectConfig'] = None
            fileName = configFolder + '%s_config.json' % (prefix)
            with open(fileName, 'w') as f:
                json.dump(c, f, indent = 1)
            cnt += 1

    for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
        for fSelect in ['L1C1', 'RF']:
            c = copy.deepcopy(template[model])
            p = dict()
            prefix = '%s_std_%s' % (model, fSelect)
            if fSelect == 'L1C1':
                p['method'] = 'LinearSVC'
                p['params'] = dict()
                p['params']['C'] = 1.0
                c['taskName'] = prefix
            elif fSelect == 'RF':
                p['method'] = 'RF'
                p['params'] = dict()
                c['taskName'] = prefix
            c['setting']['fSelectConfig'] = p
            fileName = configFolder + '%s_config.json' % (prefix)
            
            with open(fileName, 'w') as f:
                json.dump(c, f, indent=1)
            cnt += 1

    print(cnt)
