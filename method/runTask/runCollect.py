#!/usr/bin/env python3
import os
from genConfig import *

suffix = '_TwoClass'
suffix = ''
suffix = '_4T_withWG'
suffix = '_5T_Merged_withWG'
suffix = '_5T_Merged'
#suffix = '_4T'
#suffix = '_Filtered_5T_Merged'
#suffix = '_Filtered_4T'
resultFolder = '.'

if __name__ == '__main__':
    
    #for scoreName in ["MacroF1", "Accuracy", "F1_agree", "F1_oppose"]:
    for scoreName in ["Accuracy"]:
        scoreFile = './results20150628_new_%s_%s.csv' % (suffix, scoreName)
        #for framework in ["SelfTrainTest", "LeaveOneTest", "AllTrainTest"]:
        for framework in ["SelfTrainTest"]:
            for model in ["WM", "Dep_Full", "Dep_POS", "Dep_PP", "Dep_PPAll", "OM_noH", "OM_withH", "OM_stance"]:
            #for model in ["WM_LDA"]:
                configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model + suffix)
                print(len(configList))
                for name, config in configList:
                    cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
                    #print(cmd)
                    #os.system(cmd)
                #os.system('echo "" >> %s' %(scoreFile))

        
        mList = [
                ['WM', 'Dep_Full', 'Dep_POS', 'Dep_PP'],
                ['WM', 'Dep_Full', 'Dep_POS', 'Dep_PPAll'],
                ['WM', 'OM_noH'],
                ['WM', 'OM_withH'],
                ['WM', 'OM_stance'],
                ['WM', 'Dep_PPAll', 'OM_noH'],
                ['WM', 'Dep_PPAll', 'OM_withH'],
                ['WM', 'Dep_PPAll', 'OM_stance']
            ]

        for m in mList:
            name, config = genMergedConfig(m)
            cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
            print(cmd)
            os.system(cmd)
            #os.system('echo "" >> %s' %(scoreFile))


            '''
            # for mixed model 
            for model in ["OLDM_PP", "OM_withH"]:
                configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_" + model + suffix)
                print(len(configList))
                for name, config in configList:
                    #cmd = 'python3 ./clean.py %s_results.csv %s_results2.csv' % (name, name)
                    cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
                    #print(cmd)
                    #os.system(cmd)
                #os.system('echo "" >> %s' %(scoreFile))

            # for mixed model 
            for model in ["OM_withH"]:
                configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_OLDM_PP_" + model + suffix)
                print(len(configList))
                for name, config in configList:
                    #cmd = 'python3 ./clean.py %s_results.csv %s_results2.csv' % (name, name)
                    cmd = 'python3 ./CollectResult.py %s %s %s %s/%s_results.csv 0 6 >> %s' %(scoreName, framework, name, resultFolder, name, scoreFile)
                    #print(cmd)
                    #os.system(cmd)
                #os.system('echo "" >> %s' %(scoreFile))
            '''
