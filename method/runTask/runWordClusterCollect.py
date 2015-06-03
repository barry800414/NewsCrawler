#!/usr/bin/env python3
import os

scoreFile = './results20150601_tag300.csv'

if __name__ == '__main__':
    
    cnt = 0
    
    for model in ['WM', 'OLDM', 'OM', 'WM_OLDM', 'WM_OM', 'WM_OLDM_OM']:
        for pre in [None, 'std', 'norm1', 'norm2', 'binary']:
            prefix = '%s_%s_None' % (model, pre)
            resultFile = '%s_tag300_results.csv' % (prefix)
            paramFile = '%s_tag300_params.json' % (prefix)
            #cmd = 'echo "%s" >> %s.nameList' % (prefix, scoreFile) 
            cmd = 'python3 CollectResult.py testScore %s %s 0 6 >> %s' % (resultFile, paramFile, scoreFile)
            os.system(cmd)
            print(cmd)
            cnt += 1
        for fSelect in ['L1C1', 'RF']:
            prefix = '%s_std_%s' % (model, fSelect)
            resultFile = '%s_tag300_results.csv' %(prefix)
            paramFile = '%s_tag300_params.json' % (prefix)
            #cmd = 'echo "%s" >> %s.nameList' % (prefix, scoreFile) 
            cmd = 'python3 CollectResult.py testScore %s %s 0 6 >> %s' % (resultFile, paramFile, scoreFile)
            os.system(cmd)
            print(cmd)
            cnt += 1

