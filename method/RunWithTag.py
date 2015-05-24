
import sys
import os

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:', sys.argv[0], 'taskType(WM/OLDM/OLPDM) volcFile1 volcFile2 ...', file=sys.stderr)
        exit(-1)
 
    taskType = sys.argv[1]

    for volcFile in sys.argv[2:]:
        s = volcFile.rfind('/')
        e = volcFile.rfind('.')
        volcPrefix = volcFile[s+1:e]
        if taskType == 'WM':
            cmd = 'python3 ./baseline/WordModelImproved.py ./zhtNewsData/taggedLabelNews20150504.json ./baseline/config/WM_config.json %s > WM_%s_results.csv' % (volcFile, volcPrefix)
            print(cmd)
            os.system(cmd)
        elif taskType == 'OLDM':
            cmd = 'python3 ./DepBased/OneLayerPhraseDepModel.py ./zhtNewsData/OLPDM_labelNews_20150504.json ./DepBased/config/OLDM_config.json ./res/NTUSD_core.csv -v %s > OLDM_%s_results.csv' % (volcFile, volcPrefix)
            print(cmd)
            os.system(cmd)

