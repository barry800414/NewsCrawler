
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

# generating word graph
wcFolder = './WordClustering'
outFolder = './WordClustering/wordGraph'
topicList = [2, 3, 4, 5, 13]
for t in topicList:
    for k in [20]:
        cmd = 'python3 %s/WordGraph.py %s/news7852Final.vector TopK %d %s/wg7852_T%d_Top%d.mtx %s/wg7852_T%d_Top%d.volc %s/news7852Final_T%d_P40.volc' % (wcFolder, wcFolder, k, outFolder, t, k, outFolder, t, k, wcFolder, t)
        #print(cmd)
        #sender.putTask(cmd)


inFolder = outFolder
# propagate word graph
for t in topicList:
    for step in [2, 5, 10]:
        for method in ['TopK', 'TopKEachRow']:
            for value in [2, 3, 5, 10]:
                inPrefix = 'wg7852_T%d_Top20' % (t)
                outPrefix = 'wg7852_T%d_Top20_step%d_%s%d' % (t, step, method, value)
                cmd = 'python3 %s/WordProp.py %s/%s.mtx %s/%s.volc 0.75 %d %s %d %s/%s.adjList %s/%s.mtx' % (wcFolder, inFolder, inPrefix, inFolder, inPrefix, step, method, value, inFolder, outPrefix, inFolder, outPrefix)
                print(cmd)
                sender.putTask(cmd)

