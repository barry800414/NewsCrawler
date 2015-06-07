
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

sender = SendJob()

wcFolder = './WordClustering'
wordVecFile = '%s/news7852Final.vector' % (wcFolder)
fileFolder = '%s/WordCntList' % (wcFolder)
sentiFile = './res/NTUSD_core.csv'


# converting
# WM
topicList = [2, 3, 4, 5, 6, 13, 16, 'All']
for t in topicList:    
    for t1 in ['c7852']: 
        inputName = 'WM_T%s' %(t)
        taskName = 'WM_%s_T%s' %(t1, t)
        cmd = 'python3 %s/ConvertWordVector.py %s %s/%s.npy %s/%s_inVolc.txt -wc %s/%s.txt 0' %(
                    wcFolder, wordVecFile, fileFolder, taskName, fileFolder, taskName, fileFolder, inputName)
        #print(cmd)
        #sender.putTask(cmd)

# OLDM
topicList = [2, 3, 4, 5, 6, 13, 16, 'All']
for t in topicList:    
    for t1 in ['NTUSD', 'Tag']:
        for t2 in ['sW', 'flW']: 
            inputName = 'OLDM_%s_T%s_%s' %(t1, t, t2)
            taskName = 'OLDM_c7852_%s_T%s_%s' %(t1, t, t2)
            cmd = 'python3 %s/ConvertWordVector.py %s %s/%s.npy %s/%s_inVolc.txt -wc %s/%s.txt 0' %(
                    wcFolder, wordVecFile, fileFolder, taskName, fileFolder, taskName, fileFolder, inputName)
            #print(cmd)
            #sender.putTask(cmd)

# OM
for t in topicList:
    for t1 in ['c7852']:
        for t2 in ['hdW', 'opnW', 'tgW']:
            inputName = 'OM_T%s_%s' % (t, t2)
            taskName = 'OM_%s_T%s_%s' % (t1, t, t2)
            cmd = 'python3 %s/ConvertWordVector.py %s %s/%s.npy %s/%s_inVolc.txt -wc %s/%s.txt 0' %(
                    wcFolder, wordVecFile, fileFolder, taskName, fileFolder, taskName, fileFolder, inputName)
            #print(cmd)
            #sender.putTask(cmd)

# clustering

# WM
topicList = [2, 3, 4, 5, 6, 13, 16, 'All']
for t in topicList:    
    for t1 in ['c7852']:
        taskName = 'WM_%s_T%s' %(t1, t)
        cmd = 'python3 %s/WordClustering.py %s/%s.npy %s/%s_inVolc.txt %f %s/%s -v %s' %(
                wcFolder, fileFolder, taskName, fileFolder, taskName, 0.1, wcFolder, taskName, sentiFile)
        #print(cmd)
        #sender.putTask(cmd)

# OLDM
for t in topicList:    
    for t1 in ['c7852_NTUSD', 'c7852_Tag']:
        for t2 in ['sW', 'flW']:
            taskName = 'OLDM_%s_T%s_%s' %(t1, t, t2)
            cmd = 'python3 %s/WordClustering.py %s/%s.npy %s/%s_inVolc.txt %f %s/%s -v %s' %(
                    wcFolder, fileFolder, taskName, fileFolder, taskName, 0.1, wcFolder, taskName, sentiFile)
            print(cmd)
            sender.putTask(cmd)

# OM
for t in topicList:
    for t1 in ['c7852']:
        for t2 in ['hdW', 'opnW', 'tgW']:
            taskName = 'OM_%s_T%s_%s' % (t1, t, t2)
            cmd = 'python3 %s/WordClustering.py %s/%s.npy %s/%s_inVolc.txt %f %s/%s -v %s' %(
                    wcFolder, fileFolder, taskName, fileFolder, taskName, 0.1, wcFolder, taskName, sentiFile)
            print(cmd)
            sender.putTask(cmd)

