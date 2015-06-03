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
taggedFile = './engCorpus/taggedEngLabelNews.json'
depFile = './engCorpus/depParsedLabelNews.json'
taggedDepFile = './engCorpus/taggedAndDepParsedEngLabelNews.json'
dictFile = './res/NTUSD_core.csv'
#negFile = './DepBased/negPattern.json'
#patternFile = './DepBased/my_pattern.json'

scoreFile = './EN_results20150601.csv'

if __name__ == '__main__':
    sender = SendJob()
    
    cnt = 0
    
    for model in ['WM', 'OLDM']:
        for pre in [None, 'std', 'norm1', 'binary']:
            prefix = '%s_%s_None' % (model, pre)
            configFile = configFolder + 'EN_%s_config.json' % (prefix)
            resultFile = 'EN_%s_results.csv' % (prefix)
            stderrFile = 'EN_%s.stderr' % (prefix)
            WMParamFile = 'EN_WM_%s_None_params.json' % (pre)
            OLDMParamFile = 'EN_OLDM_%s_None_params.json' % (pre)
            OMParamFile = 'EN_OM_%s_None_params.json' % (pre)
            if model == 'WM':
                cmd = "python3 %s %s %s > %s 2> %s" % (pyMap[model], taggedFile, configFile, resultFile, stderrFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s > %s 2> %s" %(pyMap[model], depFile, configFile, dictFile, resultFile, stderrFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s > %s 2> %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, resultFile, stderrFile)
            elif model == 'WM_OLDM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s > %s 2> %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, resultFile, stderrFile)
            elif model == 'WM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OM %s -tp %s -ng %s > %s 2> %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OMParamFile, patternFile, negFile, resultFile, stderrFile)
            elif model == 'WM_OLDM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -OM %s -tp %s -ng %s > %s 2> %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, OMParamFile, patternFile, negFile, resultFile, stderrFile)
            
            
            paramFile = 'EN_%s_params.json' % (prefix)
            #cmd += '; echo "EN_%s" >> %s.1; python3 CollectEngResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            #os.system(cmd)
            print(cmd)
            sender.putTask(cmd)
            cnt += 1
    
    
    for model in ['WM', 'OLDM']:
        for fSelect in ['L1C1', 'RF']:
            prefix = '%s_None_%s' % (model, fSelect)
            configFile = configFolder + 'EN_%s_config.json' % (prefix)
            resultFile = 'EN_%s_results.csv' %(prefix)
            stderrFile = 'EN_%s.stderr' % (prefix)
            WMParamFile = 'EN_WM_None_%s_params.json' % (fSelect)
            OLDMParamFile = 'EN_OLDM_None_%s_params.json' % (fSelect)
            OMParamFile = 'EN_OM_None_%s_params.json' % (fSelect)
            if model == 'WM':
                cmd = "python3 %s %s %s > %s 2> %s" % (pyMap[model], taggedFile, configFile, resultFile, stderrFile)
            elif model == 'OLDM':
                cmd = "python3 %s %s %s %s > %s 2> %s" %(pyMap[model], depFile, configFile, dictFile, resultFile, stderrFile) 
            elif model == 'OM':
                cmd = "python3 %s %s %s %s %s %s > %s 2> %s" % (pyMap[model], depFile, configFile, patternFile, negFile, dictFile, resultFile, stderrFile)
            elif model == 'WM_OLDM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s > %s 2> %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, resultFile, stderrFile)
            elif model == 'WM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OM %s -tp %s -ng %s > %s 2> %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OMParamFile, patternFile, negFile, resultFile, stderrFile)
            elif model == 'WM_OLDM_OM':
                cmd = "python3 %s %s %s %s -WM %s -OLDM %s -OM %s -tp %s -ng %s > %s 2> %s" % (pyMap[model], taggedDepFile, configFile, dictFile, WMParamFile, OLDMParamFile, OMParamFile, patternFile, negFile, resultFile, stderrFile)
            
            paramFile = 'EN_%s_params.json' % (prefix)
            #cmd += '; echo "%s" >> %s; python3 CollectResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            #cmd += '; echo "EN_%s" >> %s.1; python3 CollectEngResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            #os.system(cmd)
            print(cmd)
            sender.putTask(cmd)
            cnt += 1
    print(cnt)

