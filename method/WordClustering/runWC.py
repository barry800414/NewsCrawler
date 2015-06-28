
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
outVolcFolder = './WordClustering/volc'
sentiFile = './res/NTUSD_core.csv'

# clustering
# WM
topicList = [2, 3, 4, 5, 13]
for t in topicList:    
    for p in range(1, 10):
        percent = p * 0.1
        outName = 'news7852Final_T%d_P40_p%d.volc' % (t, p*10)
        cmd = 'python3 %s/WordClustering.py %s/news7852Final_T%d_P40.npy %s/news7852Final_T%d_P40.volc %f %s/%s -v %s' %(
                wcFolder, wcFolder, t, wcFolder, t, percent, outVolcFolder, outName, sentiFile)
        print(cmd)
        sender.putTask(cmd)

