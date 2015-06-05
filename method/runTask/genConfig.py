

import copy
import json

configFolder = './config/'

mergeTemplate = {
    "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
    "preprocess": None,
    "minCnt": 2,
    "taskName": "OM_all_norm1",
    "setting":{
        "targetScore": "MacroF1",
        "clfList": ["LinearSVM"],
        "randSeedList": [1, 2, 3, 4, 5],
        "testSize": 0.2,
        "n_folds": 3,
        "fSelectConfig": None
    }
}

# default config of each model
defaultConfig={
        "WM": {
            "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": None,
            "minCnt": 2,
            "params":{ 
                "feature": ["tf"],
                "allowedPOS": [["VA", "VV", "NN", "NR", "AD", "JJ"]]
            },
            "setting":{
                "targetScore": "MacroF1",
                "clfList": ["LinearSVM"],
                "randSeedList": [1, 2, 3, 4, 5],
                "testSize": 0.2,
                "n_folds": 3,
                "fSelectConfig": None
            },
            "fSelectConfig": None,
            "volc": None
        },
        "OLDM": {
            "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": None,
            "minCnt": 2,
            "params":{ 
                "seedWordType": [
                    {"type": "tag", "allow": ["NR","NN","NP"]}
                ],
                "firstLayerType": [ 
                    {"type": "word", "allow": "NTUSD_core"} 
                ]
            },
            "setting":{
                "targetScore": "MacroF1",
                "clfList": ["LinearSVM"],
                "randSeedList": [1, 2, 3, 4, 5],
                "testSize": 0.2,
                "n_folds": 3,
                "fSelectConfig": None
            },
            "fSelectConfig": None,
            "volc": None,
            "phrase": None
        },
        "OM": {
            "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": None,
            "minCnt": 2,
            "params":{ 
                "keyTypeList": [["H", "T", "HT"]],
                "opnNameList": [None],
                "negSepList": [[True]]
            },
            "setting":{
                "targetScore": "MacroF1",
                "clfList": ["LinearSVM"],
                "randSeedList": [1, 2, 3, 4, 5],
                "testSize": 0.2,
                "n_folds": 3,
                "fSelectConfig": None
            },
            "volc": None,
            "phrase": None
        },
        'WM_OLDM': mergeTemplate,
        'WM_OM': mergeTemplate,
        'WM_OLDM_OM': mergeTemplate
}


# generating configs for word clustering 
volcFolder = './WordClustering/volc'
topicList = [2, 3, 4, 5, 6, 13, 16, 'all']
volcFileConfig = { "WM": dict(), "OLDM": dict(), "OM": dict() }

# for WM
c = volcFileConfig['WM']
for type in ["c7852F"]:
    c[type] = dict()
    for t in topicList:
        c[type][t] = dict()
        c[type][t]['main'] = '%s/%s_WM_T%s.volc' % (volcFolder, type, str(t))

# for OLDM
c = volcFileConfig['OLDM']
for type in ['c7852F_NTUSD', 'c7852F_Tag']:
    c[type] = dict()
    for t in topicList:
        c[type][t] = dict()
        c[type][t]['seed'] = '%s/%s_OLDM_T%s_sW.volc' % (volcFolder, type, str(t))
        c[type][t]['firstLayer'] = '%s/%s_OLDM_T%s_flW.volc' % (volcFolder, type, str(t))

# for OM
c = volcFileConfig['OM']
for type in ['c7852F']:
    c[type] = dict()
    for t in topicList:
        c[type][t] = dict()
        c[type][t]['holder'] = '%s/%s_OM_T%s_hdW.volc' % (volcFolder, type, str(t))
        c[type][t]['opinion'] = '%s/%s_OM_T%s_opnW.volc' % (volcFolder, type, str(t))
        c[type][t]['target'] = '%s/%s_OM_T%s_tgW.volc' % (volcFolder, type, str(t))

#print(volcFileConfig)

# configuration for search parameters (one parameter a time)
iterConfig={
    "WM": [
        { "path": ["preprocess"], 
            "params": {"None": None,
                       "std":    { "method": "std", "params": { "with_mean": False, "with_std": True }}, 
                       "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                       "norm1":  { "method": "norm", "params": { "norm": "l1" }}
                       }
            },

        { "path": ["setting", "fSelectConfig"],
            "params": { "RF": { "method": "RF", "params": dict() },
                        "L1C1": { "method": "LinearSVC", "params": {"C": 1.0}}
                }
            },

        { "path": ["setting", "clfList"], 
            "params": { "MaxEnt": ["MaxEnt"] }
            },
        
        { "path": ["params", "feature"], 
            "params": { "01": ["0/1"], "tfidf": ["tfidf"] } 
            },
        #{ "path": ["volc"],
        #    "params": volcFileConfig['WM']
        #}
    ],
    "OLDM" :[
        { "path": ["preprocess"], 
            "params": {"None": None,
                       "std":    { "method": "std", "params": { "with_mean": False, "with_std": True }}, 
                       "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                       "norm1":  { "method": "norm", "params": { "norm": "l1" }}
                       }
            },

        { "path": ["setting", "fSelectConfig"],
            "params": { "RF": { "method": "RF", "params": dict() },
                    "L1C1": { "method": "LinearSVC", "params": {"C": 1.0}}
                }
            },

        { "path": ["setting", "clfList"], 
            "params": { "MaxEnt": ["MaxEnt"] }
            },
            
        { "path": ["params", "firstLayerType"],
            "params": { "tag": [{"type": "tag", "allow": ["VV","JJ","VA"]}] }
            },
        { "path": ["volc"],
            "params": volcFileConfig['OLDM']
        }

    ],
    "OM":[  
        { "path": ["preprocess"], 
            "params": { "None": None,
                        "std":    { "method": "std", "params": { "with_mean": False, "with_std": True }}, 
                        "binary": { "method": "binary", "params": { "threshold": 0.0 }},
                        "norm1":  { "method": "norm", "params": { "norm": "l1" }}
                       }
            },
        { "path": ["setting", "fSelectConfig"],
            "params": { "RF": { "method": "RF", "params": dict() },
                    "L1C1": { "method": "LinearSVC", "params": {"C": 1.0}}
                }
            },

        { "path": ["setting", "clfList"], 
            "params": { "MaxEnt": ["MaxEnt"] }
            },

        { "path": ["params", "keyTypeList"], 
            "params": { "T": [["T"]], "H": [["H"]], "HT":[["HT"]], "HOT": [["HOT"]], 
                "OT": [["OT"]], "HO":[["HO"]], "all": [["H", "T", "OT", "HO", "HOT", "HT"]]}
            },

        { "path": ["params", "negSepList"], 
            "params": { "negFalse": [[False]], "negBoth": [[True, False]]}
            },
        { "path": ["volc"],
            "params": volcFileConfig['OM']
        }

    ]
}

nameList= {
    #"WM": [ "pN", "fN", "LinearSVM", "tf", "vN"],
    "WM": [ "pN", "fN", "LinearSVM", "tf"],
    "OLDM":  [ "pN", "fN", "LinearSVM", "NTUSD", "vN"],
    "OM": [ "pN", "fN", "LinearSVM", "H-T-HT", "negTrue", "vN"]
}



def genConfig(defaultConfig, iterConfig, nameList, prefix):
    configList = list()
    for i in range(0, len(iterConfig)):
        path = iterConfig[i]["path"]
        params = iterConfig[i]["params"]
        for pName, p in params.items():
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

def mergeName(prefix, nameList):
    outStr = str(prefix)
    for n in nameList:
        outStr += '_' + n
    return outStr


if __name__ == '__main__':
    for model in ["WM", "OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model)
        print(len(configList))
        for name, config in configList:
            with open(configFolder + name + '_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            print(name)
            #print(config, '\n')
    
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
