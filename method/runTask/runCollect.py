#!/usr/bin/env python3
import os
from genConfig import *

scoreFile = './results20150611_allTopics.csv'
resultFolder = '/tmp2/weiming/file20150611'

if __name__ == '__main__':
    #for framework in ["SelfTrainTest", "LeaveOneTest", "AllTrainTest"]:
    for framework in ["SelfTrainTest"]:
        for model in ["WM", "OLDM", "OM"]:
            #configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model + "_filtered")
            configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model)
            print(len(configList))
            for name, config in configList:
                cmd = 'python3 ./CollectResult.py testScore %s %s %s/%s_results.csv 0 6 >> %s' %(framework, name, resultFolder, name, scoreFile)
                print(cmd)
                os.system(cmd)

    # for mixed model 
    #for framework in ["SelfTrainTest", "LeaveOneTest", "AllTrainTest"]:
    for framework in ["SelfTrainTest"]:
        for model in ["OLDM", "OM"]:
            #configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_" + model + "_filtered")
            configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], "WM_" + model)

            print(len(configList))
            for name, config in configList:
                #cmd = 'python3 ./clean.py %s_results.csv %s_results2.csv' % (name, name)
                cmd = 'python3 ./CollectResult.py testScore %s %s %s/%s_results.csv 0 6 >> %s' %(framework, name, resultFolder, name, scoreFile)
                
                print(cmd)
                os.system(cmd)
   
    # for mixed model 
    #for framework in ["SelfTrainTest", "LeaveOneTest", "AllTrainTest"]:
    for framework in ["SelfTrainTest"]:
        for model in ["OM"]:
            #configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = "WM_OLDM_" + model + "_filtered")
            configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], "WM_OLDM_" + model)

            print(len(configList))
            for name, config in configList:
                #cmd = 'python3 ./clean.py %s_results.csv %s_results2.csv' % (name, name)
                cmd = 'python3 ./CollectResult.py testScore %s %s %s/%s_results.csv 0 6 >> %s' %(framework, name, resultFolder, name, scoreFile)

                print(cmd)
                os.system(cmd)
