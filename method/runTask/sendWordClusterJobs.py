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
volcFile = './WordClustering/cluster7852_tag300.volc'
scoreFile = './results20150601.csv'

if __name__ == '__main__':
    sender = SendJob()
    
    cnt = 0
    
    #for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
    #for model in ['WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
    for model in ['WM']:
        #for pre in [None, 'std', 'norm1', 'norm2', 'binary']:
        for pre in [None]:
            prefix = '%s_%s_None' % (model, pre)
            configFile = configFolder + '%s_config.json' % (prefix)
            resultFile = '%s_tag300_results.csv' % (prefix)
            WMParamFile = 'WM_%s_None_tag300_params.json' % (pre)
            OLDMParamFile = 'OLDM_%s_None_tag300_params.json' % (pre)
            OMParamFile = 'OM_%s_None_tag_300_params.json' % (pre)
            if model == 'WM':
                cmd = "python3 %s %s %s %s > %s" % (pyMap[model], taggedFile, configFile, volcFile, resultFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s -v %s > %s" %(pyMap[model], depFile, configFile, dictFile, volcFile, resultFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s -v %s > %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, volcFile, resultFile)
            elif model == 'WM_OLDM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -v %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, volcFile, resultFile)
            elif model == 'WM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OM %s -tp %s -ng %s -v %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OMParamFile, patternFile, negFile, volcFile, resultFile)
            elif model == 'WM_OLDM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -OM %s -tp %s -ng %s -v %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, OMParamFile, patternFile, negFile, volcFile, resultFile)
            
            
            paramFile = '%s_tag300_params.json' % (prefix)
            cmd += '; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (resultFile, paramFile, scoreFile)
            print(cmd)
            sender.putTask(cmd)
            cnt += 1
    '''
    #for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
    for model in ['WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
        for fSelect in ['L1C1', 'RF']:
            prefix = '%s_std_%s' % (model, fSelect)
            configFile = configFolder + '%s_config.json' % (prefix)
            resultFile = '%s_tag300_results.csv' %(prefix)
            WMParamFile = 'WM_std_%s_tag300_params.json' % (fSelect)
            OLDMParamFile = 'OLDM_std_%s_tag300_params.json' % (fSelect)
            OMParamFile = 'OM_std_%s_tag300_params.json' % (fSelect)
            if model == 'WM':
                cmd = "python3 %s %s %s %s > %s" % (pyMap[model], taggedFile, configFile, volcFile, resultFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s -v %s > %s" %(pyMap[model], depFile, configFile, dictFile, volcFile, resultFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s -v %s > %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, volcFile, resultFile)
            elif model == 'WM_OLDM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -v %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, volcFile, resultFile)
            elif model == 'WM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OM %s -tp %s -ng %s -v %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OMParamFile, patternFile, negFile, volcFile, resultFile)
            elif model == 'WM_OLDM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -OM %s -tp %s -ng %s -v %s > %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, OMParamFile, patternFile, negFile, volcFile, resultFile)
            
            paramFile = '%s_tag300_params.json' % (prefix)
            cmd += '; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (resultFile, paramFile, scoreFile)
            print(cmd)
            sender.putTask(cmd)
            cnt += 1
    '''
    print(cnt)

