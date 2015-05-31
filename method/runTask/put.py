#!/usr/bin/env python3
from multiprocessing.managers import BaseManager

class QueueManager(BaseManager):
    pass
class SendJob:
    def __init__():
        QueueManager.register('get_queue')
        port = 3333
        self.m = QueueManager(address=('140.112.187.33', 3333), authkey=b'barry800414')
        self.m.connect()
        self.queue = m.get_queue()

    def putTask(cmd):
        self.queue.put(cmd)

if __name__ == '__main__':
    
    # do anything you want to put the item into queue
    # eg: queue.put('example')

    for i in range(10):
        queue.put(i)
