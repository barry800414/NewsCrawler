#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
import os
from genConfig import *

class QueueManager(BaseManager):
    pass
class SendJob:
    def __init__(self):
        QueueManager.register('get_queue')
        port = 3333
        self.m = QueueManager(address=('140.112.187.33', 3333), authkey=b'barry800414')
        self.m.connect()
        self.queue = self.m.get_queue()

    def putTask(self, cmd):
        self.queue.put(cmd)

pyMap = { 
        "WM": "./baseline/WordModel.py", 
        "OLDM": "./DepBased/OneLayerDepModel.py", 
        "OM": "./DepBased/OpinionModel.py",
        "merged": "./DepBased/MergedModel.py",
}
configFolder = './config/'
taggedFile = './zhtNewsData/taggedLabelNewsFinal_long.json'
depFile = './zhtNewsData/DepParsedLabelNewsFinal_short.json'
labelNewsFile = './zhtNewsData/taggedLabelNewsFinal_long.json' #FIXME

#taggedDepFile = './zhtNewsData/taggedAndDepParsedLabelNews20150504.json'
dictFile = './res/NTUSD_core.csv'
negFile = './DepBased/negPattern.json'
patternFile = './DepBased/my_pattern.json'

scoreFile = './results20150601.csv'


if __name__ == '__main__':
    sender = SendJob()
    
    # for single model
    for model in ["WM", "OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model)
        print(len(configList))
        for taskName, config in configList:
            configFile = configFolder + taskName + '_config.json'
            resultFile = '%s_results.csv' % (taskName)
            if model == 'WM':
                cmd = "python3 %s %s %s > %s" % (pyMap[model], taggedFile, configFile, resultFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s > %s" %(pyMap[model], depFile, configFile, dictFile, resultFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s > %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, resultFile)
            #print(cmd)
            #sender.putTask(cmd)

    # for mixed model 
    WMPickleFile = 'WM_pN_fN_LinearSVM_tfidf_vN'
    for model in ["OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_" + model)
        print(len(configList))
        for taskName, config in configList:
            configFile = configFolder + taskName + '_config.json'
            resultFile = '%s_results.csv' % (taskName)
            cmd = "python3 %s %s %s -WM %s -%s %s > %s" % (pyMap['merged'], labelNewsFile, configFile, 
                    WMPickleFile, model, taskName[len("WM_"):], resultFile)
            
            print(cmd)
            sender.putTask(cmd)
   
    # for mixed model 
    OLDMPickleFile = 'OLDM_pN_fN_LinearSVM_tag_vN'
    for model in ["OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_OLDM_" + model)
        print(len(configList))
        for taskName, config in configList:
            configFile = configFolder + taskName + '_config.json'
            resultFile = '%s_results.csv' % (taskName)
            cmd = "python3 %s %s %s -WM %s -OLDM %s -%s %s > %s" % (pyMap['merged'], labelNewsFile, configFile, 
                    WMPickleFile, OLDMPickleFile, model, taskName[len("WM_OLDM_"):], resultFile)

            print(cmd)
            sender.putTask(cmd)
   


if __name__ == '__main2__':
    for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
    #for model in ['WM', 'OLDM', 'OM']:
    #for model in ['WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
        for pre in [None, 'std', 'norm1', 'norm2', 'binary']:
        #for pre in ['binary']:
            prefix = '%s_%s_None' % (model, pre)
            configFile = configFolder + '%s_config.json' % (prefix)
            resultFile = '%s_results.csv' % (prefix)
            WMParamFile = 'WM_%s_None_params.json' % (pre)
            OLDMParamFile = 'OLDM_%s_None_params.json' % (pre)
            OMParamFile = 'OM_%s_None_params.json' % (pre)
            if model == 'WM':
                cmd = "python3 %s %s %s > %s" % (pyMap[model], taggedFile, configFile, resultFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s > %s" %(pyMap[model], depFile, configFile, dictFile, resultFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s > %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, resultFile)
            elif model == 'WM_OLDM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, resultFile)
            elif model == 'WM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OM %s -tp %s -ng %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OMParamFile, patternFile, negFile, resultFile)
            elif model == 'WM_OLDM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -OM %s -tp %s -ng %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, OMParamFile, patternFile, negFile, resultFile)
            
            
            paramFile = '%s_params.json' % (prefix)
            #cmd += '; echo "%s" >> %s; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            cmd = 'echo "%s" >> %s.1; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            os.system(cmd)
            print(cmd)
            #sender.putTask(cmd)
            cnt += 1
    
    
    for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
    #for model in ['WM', 'OLDM', 'OM']:
    #for model in ['WM_OLDM']:
        for fSelect in ['L1C1', 'RF']:
            prefix = '%s_std_%s' % (model, fSelect)
            configFile = configFolder + '%s_config.json' % (prefix)
            resultFile = '%s_results.csv' %(prefix)
            WMParamFile = 'WM_std_%s_params.json' % (fSelect)
            OLDMParamFile = 'OLDM_std_%s_params.json' % (fSelect)
            OMParamFile = 'OM_std_%s_params.json' % (fSelect)
            if model == 'WM':
                cmd = "python3 %s %s %s > %s" % (pyMap[model], taggedFile, configFile, resultFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s > %s" %(pyMap[model], depFile, configFile, dictFile, resultFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s > %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, resultFile)
            elif model == 'WM_OLDM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, resultFile)
            elif model == 'WM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OM %s -tp %s -ng %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OMParamFile, patternFile, negFile, resultFile)
            elif model == 'WM_OLDM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -OM %s -tp %s -ng %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, OMParamFile, patternFile, negFile, resultFile)
            
            paramFile = '%s_params.json' % (prefix)
            #cmd += '; echo "%s" >> %s; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            cmd = 'echo "%s" >> %s.1; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            os.system(cmd)
            print(cmd)
            #sender.putTask(cmd)
            cnt += 1
    print(cnt)

