#!/usr/bin/env python3
from multiprocessing.managers import BaseManager
import sys
import os

# declare the QueueManager like server
class QueueManager(BaseManager):
    pass
# register method get_queue()
QueueManager.register('get_queue')

if __name__ == '__main__':
    port = 3333
    server_address = ('140.112.187.33', port)
    authkey = b'barry800414'
    m = QueueManager(address = server_address, authkey = authkey)
    print('Connecting to server (port:%d) ...' % (port), file=sys.stderr)
    m.connect()
    queue = m.get_queue()
    
    while True:
        try:
            print('Waiting for next job ...', file=sys.stderr)
            sys.stderr.flush()

            item = queue.get()
            print('Got a task from queue', file=sys.stderr)
            sys.stderr.flush()

        except KeyboardInterrupt: # Ctrl + C interrupt (i.e. want to exit)
            break
        
        ## do anything about your item
        try:
            print('Doing the task...', file=sys.stderr)
            sys.stderr.flush()

            print(item + '\n')
            sys.stdout.flush()
            print(item, file=sys.stderr)
            sys.stderr.flush()
            os.system(item)
        except KeyboardInterrupt: # Ctrl + C interrupt (i.e. want to exit)
            # requeue your item, because fail to finish it
            queue.put(item)
            # break the while loop
            break
        except Exception as e:
            print(e, file=sys.stderr)
            sys.stderr.flush()

            pass ## catch the other exception, and handle it
