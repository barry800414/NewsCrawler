#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
import os

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
        "WM_OLDM": "./DepBased/MergedModel.py",
        "WM_OM": "./DepBased/MergedModel.py",
        "WM_OLDM_OM": "./DepBased/MergedModel.py"
}
configFolder = './config/'
taggedFile = './zhtNewsData/taggedLabelNews20150504.json'
depFile = './zhtNewsData/OLPDM_labelNews_20150504.json'
taggedDepFile = './zhtNewsData/taggedAndDepParsedLabelNews20150504.json'
dictFile = './res/NTUSD_core.csv'
negFile = './DepBased/negPattern.json'
patternFile = './DepBased/my_pattern.json'

scoreFile = './results20150601.csv'

if __name__ == '__main__':
    sender = SendJob()
    
    cnt = 0
    
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

