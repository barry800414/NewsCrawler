

import copy
import json

configFolder = './config/'

mergeTemplate = {
    "toRun": ["SelfTrainTest"],
    "preprocess": None,
    "dataset": "engDebate",
    "modelName": "EN_WM_None_seed1",
    "minCnt": 2,
    "sampling":{
        "randSeed": 1,
        "docNumForEachTopic": {
            "1":{ 
                "agree": 275, "oppose": 275
            },
            "2":{
                "agree": 265, "oppose": 265
            },
            "3":{
                "agree": 423, "oppose": 423
            },
            "5":{
                "agree": 153, "oppose": 153
            }
        }
    },
    "setting":{
        "targetScore": "Accuracy",
        "clfList": ["LinearSVM"],
        "randSeedList": [1],
        "testSize": 10,
        "n_folds": 5,
    }
}

template={
        "WM": {    
            "toRun": ["SelfTrainTest"],
            "preprocess": None,
            "dataset": "engDebate",
            "modelName": "EN_WM_None_seed1",
            "minCnt": 2,
            "sampling":{
                "randSeed": 1,
                "docNumForEachTopic": {
                    "1":{ 
                        "agree": 275, "oppose": 275
                    },
                    "2":{
                        "agree": 265, "oppose": 265
                    },
                    "3":{
                        "agree": 423, "oppose": 423
                    },
                    "5":{
                        "agree": 153, "oppose": 153
                    }
                }
            },
            "params":{ 
                "feature": ["tf"],
                "allowedPOS": [["JJ", "NN", "RB", "VB"]]
            },
            "setting":{
                "targetScore": "Accuracy",
                "clfList": ["LinearSVM"],
                "randSeedList": [1],
                "testSize": 10,
                "n_folds": 5,
            }
        },
        "OLDM": {
            "toRun": ["SelfTrainTest"],
            "preprocess": None,
            "dataset": "engDebate",
            "modelName": "EN_OLDM_None_seed1",
            "minCnt": 2,
            "sampling":{
                "randSeed": 1,
                "docNumForEachTopic": {
                    "1":{ 
                        "agree": 275, "oppose": 275
                    },
                    "2":{
                        "agree": 265, "oppose": 265
                    },
                    "3":{
                        "agree": 423, "oppose": 423
                    },
                    "5":{
                        "agree": 153, "oppose": 153
                    }
                }
            },
            "params":{ 
                "seedWordType": [
                    {"type": "tag", "allow": ["NN", "NP", "NNP"]}
                ],
                "firstLayerType": [ 
                    {"type": "tag", "allow": ["JJ","VB"]} 
                ]
            },
            "setting":{
                "targetScore": "Accuracy",
                "clfList": ["LinearSVM"],
                "randSeedList": [1],
                "testSize": 10,
                "n_folds": 5,
            }
        },
        'WM_OLDM': mergeTemplate,
}


if __name__ == '__main__':
    cnt = 0

    # configs for test feature normalization
    for model in ['WM', 'OLDM']:
        for pre in [None, 'std', 'norm1', 'binary']:
            c = copy.deepcopy(template[model])
            if c['preprocess'] == None:
                c['preprocess'] = dict()
            p = c['preprocess']
            prefix = 'EN_%s_%s_None' % (model, pre)
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

    # test for feature selection
    for model in ['WM', 'OLDM']:
        for fSelect in ['L1C1', 'RF']:
            c = copy.deepcopy(template[model])
            p = dict()
            prefix = 'EN_%s_None_%s' % (model, fSelect)
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
