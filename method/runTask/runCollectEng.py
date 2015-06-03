#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
import os

configFolder = './config/'
taggedFile = './engCorpus/taggedEngLabelNews.json'
depFile = './engCorpus/depParsedLabelNews.json'
taggedDepFile = './engCorpus/taggedAndDepParsedEngLabelNews.json'
dictFile = './res/NTUSD_core.csv'
#negFile = './DepBased/negPattern.json'
#patternFile = './DepBased/my_pattern.json'

scoreFile = './EN_results20150601.csv'

if __name__ == '__main__':
    cnt = 0
    
    for model in ['WM', 'OLDM']:
        for pre in [None, 'std', 'norm1', 'binary']:
            prefix = '%s_%s_None' % (model, pre)
            configFile = configFolder + 'EN_%s_config.json' % (prefix)
            resultFile = 'EN_%s_results.csv' % (prefix)
            stderrFile = 'EN_%s.stderr' % (prefix)
            
            paramFile = 'EN_%s_params.json' % (prefix)
            cmd = 'echo "%s" >> %s; python3 CollectEngResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            os.system(cmd)
            print(cmd)
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
            paramFile = 'EN_%s_params.json' % (prefix)
            cmd = 'echo "%s" >> %s; python3 CollectEngResult.py testScore %s %s 0 6 >> %s' % (prefix, scoreFile, resultFile, paramFile, scoreFile)
            os.system(cmd)
            print(cmd)
            cnt += 1
    print(cnt)

