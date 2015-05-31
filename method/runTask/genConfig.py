

import copy
import json

configFolder = './config/'

mergeTemplate = {
    "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
    "preprocess": {
        "method": "std",
        "params": { 
            "with_mean": False,
            "with_std": True
        }
    },
    "minCnt": 2,
    "modelName": "OM_all_norm1",
    "dataset": "zhtNews",
    "setting":{
        "targetScore": "MacroF1",
        "clfList": ["MaxEnt", "LinearSVM"],
        "randSeedList": [1, 2, 3, 4, 5],
        "testSize": 0.2,
        "n_folds": 3
    }
}

template={
        "WM": {
            "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": {
                "method": "std",
                "params": { 
                    "with_mean": False,
                    "with_std": True
                }
            },
            "dataset": "zhtNews",
            "minCnt": 2,
            "params":{ 
                "feature": ["0/1", "tf", "tfidf"],
                "allowedPOS": [["VA", "VV", "NN", "NR", "AD", "JJ"]]
            },
            "setting":{
                "targetScore": "MacroF1",
                "clfList": ["MaxEnt", "LinearSVM"],
                "randSeedList": [1, 2, 3, 4, 5],
                "testSize": 0.2,
                "n_folds": 3
            }
        },
        "OLDM": {
            "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": {
                "method": "std",
                "params": { 
                    "with_mean": False,
                    "with_std": True
                }
            },
            "dataset": "zhtNews",
            "minCnt": 2,
            "params":{ 
                "seedWordType": [
                    {"type": "tag", "allow": ["NR","NN","NP"]}
                ],
                "firstLayerType": [ 
                    {"type": "word", "allow": "NTUSD_core"}, 
                    {"type": "tag", "allow": ["VV","JJ","VA"]} 
                ]
            },
            "setting":{
                "targetScore": "MacroF1",
                "clfList": ["MaxEnt", "LinearSVM"],
                "randSeedList": [1, 2, 3, 4, 5],
                "testSize": 0.2,
                "n_folds": 3,
            }
        },
        "OM": {
            "toRun": ["SelfTrainTest", "AllTrainTest", "LeaveOneTest"],
            "preprocess": {
                "method": "std",
                "params": { 
                    "with_mean": False,
                    "with_std": True
                }
            },
            "dataset": "zhtNews",
            "minCnt": 2,
            "params":{ 
                "keyTypeList": [["H", "T", "HT", "HOT", "OT", "HO"]],
                "opnNameList": [None],
                "negSepList": [[False], [True], [True, False]]
            },
            "setting":{
                "targetScore": "MacroF1",
                "clfList": ["MaxEnt", "LinearSVM"],
                "randSeedList": [1, 2, 3, 4, 5],
                "testSize": 0.2,
                "n_folds": 3,
            }
        },
        'WM_OLDM': mergeTemplate,
        'WM_OM': mergeTemplate,
        'WM_OLDM_OM': mergeTemplate
}


if __name__ == '__main__':
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
                c['modelName'] = prefix
            elif pre == 'norm1':
                p['method'] = 'norm'
                p['params'] = dict()
                p['params']['norm'] = 'l1'
                c['modelName'] = prefix
            elif pre == 'norm2':
                p['method'] = 'norm'
                p['params'] = dict()
                p['params']['norm'] = 'l2'
                c['modelName'] = prefix
            elif pre == 'binary':
                if model == 'WM':
                    c['params']['feature'] = ['tf']
                if model == 'OM':
                    c['params']['negSepList'] = [[True]]
                p['method'] = 'binary'
                p['params'] = dict()
                p['params']['threshold'] = 0.0
                c['modelName'] = prefix
            elif pre == None:
                c['preprocess'] = None
                c['modelName'] = prefix
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
                c['modelName'] = prefix
            elif fSelect == 'RF':
                p['method'] = 'RF'
                p['params'] = dict()
                c['modelName'] = prefix
            c['setting']['fSelectConfig'] = p
            fileName = configFolder + '%s_config.json' % (prefix)
            
            with open(fileName, 'w') as f:
                json.dump(c, f, indent=1)
            cnt += 1

    print(cnt)
