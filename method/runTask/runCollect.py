#!/usr/bin/env python3
import os
from genConfig import *

suffix = '_TwoClass'
suffix = ''
suffix = '_4T_withWG'
suffix = '_5T_Merged_withWG'
#suffix = '_5T_Merged'
#suffix = '_Filtered_5T_Merged'
#suffix = '_Filtered_4T'
resultFolder = '.'

if __name__ == '__main__':
    
    for scoreName in ["MacroF1", "Accuracy", "F1_agree", "F1_oppose"]:
    #for scoreName in ["MacroF1"]:
        scoreFile = './results20150623%s_%s.csv' % (suffix, scoreName)
        #for framework in ["SelfTrainTest", "LeaveOneTest", "AllTrainTest"]:
        for framework in ["SelfTrainTest"]:
            for model in ["WM", "OLDM", "OM"]:
                configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model + suffix)
                print(len(configList))
                for name, config in configList:
                    cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
                    #print(cmd)
                    #os.system(cmd)
                #os.system('echo "" >> %s' %(scoreFile))

            # for mixed model 
            for model in ["OLDM", "OM"]:
                configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_" + model + suffix)
                print(len(configList))
                for name, config in configList:
                    #cmd = 'python3 ./clean.py %s_results.csv %s_results2.csv' % (name, name)
                    cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
                    print(cmd)
                    os.system(cmd)
                os.system('echo "" >> %s' %(scoreFile))

            # for mixed model 
            for model in ["OM"]:
                configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_OLDM_" + model + suffix)
                print(len(configList))
                for name, config in configList:
                    #cmd = 'python3 ./clean.py %s_results.csv %s_results2.csv' % (name, name)
                    cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
                    print(cmd)
                    os.system(cmd)
                os.system('echo "" >> %s' %(scoreFile))

