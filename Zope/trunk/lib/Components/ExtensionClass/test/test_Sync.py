from Sync import Synchronized
import thread
from random import random
from time import sleep

class P(Synchronized):

    def __init__(self,*args,**kw):
        self.count=0

    def inc(self):
            c = self.count
            if random() > 0.7:
                sleep(1)
            self.count = self.count + 1
            return c, self.count

    def incn(self,n):
            c = self.count
            for i in range(n):
                self.inc()
            return c, self.count
        
p = P(1, 2, spam=3)

def test():
    for i in range(8):
        n = 3
        old, new = p.incn(n)
        if old + n != new:
            print 'oops'
        sleep(2)
    thread_finished()

def thread_finished(lock=thread.allocate_lock()):
    global num_threads
    lock.acquire()
    num_threads = num_threads - 1
    lock.release()

num_threads = 8
for i in range(num_threads):
    thread.start_new_thread(test, ())

while num_threads > 0:
    sleep(1)
