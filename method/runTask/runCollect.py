#!/usr/bin/env python3
import os
from genConfig import *

scoreFile = './results20150607.csv'

if __name__ == '__main__':
    for model in ["WM", "OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model)
        print(len(configList))
        for name, config in configList:
            cmd = 'python3 ./CollectResult.py testScore SelfTrainTest %s %s_results.csv 0 6 >> %s' %(name, name, scoreFile)
            print(cmd)
            os.system(cmd)

    for model in ["WM", "OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model)
        print(len(configList))
        for name, config in configList:
            cmd = 'python3 ./CollectResult.py testScore LeaveOneTest %s %s_results.csv 0 6 >> %s' %(name, name, scoreFile)
            print(cmd)
            os.system(cmd)

    for model in ["WM", "OLDM", "OM"]:
        configList = genConfig(defaultConfig[model], iterConfig[model], nameList[model], prefix = model)
        print(len(configList))
        for name, config in configList:
            cmd = 'python3 ./CollectResult.py testScore AllTrainTest %s %s_results.csv 0 6 >> %s' %(name, name, scoreFile)
            print(cmd)
            os.system(cmd)

