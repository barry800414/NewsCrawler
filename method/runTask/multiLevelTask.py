#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
import os
from genConfig import *

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
seed = 1
for t in [2,3,4,5,13]:
    for fold in range(0, 10):
        cmd = 'cd ./MultiLevel/svm-sle2/; python3 run_training.py %d %d %d' % (t, fold, seed)
        print(cmd)
        sender.putTask(cmd)
