import threading
import pickle
import os

class NoTask(Exception):
    pass

class taskqueue:
    def __init__(self, base):
        self._base = base
        self._lock = threading.Lock()
        self._fetched = dict()
    
    def empty(self):
        with self._lock:
            return self._base.empty()
    
    def __len__(self):
        with self._lock:
            return len(self._base)
    
    def append(self, x):
        with self._lock:
            for i in reversed(range(len(self._base))):
                if self._base[i] == x:
                    if not self._istaskfetched(i):
                        del self._base[i]
            return self._base.append(x)
    
    def fetchtask(self):
        with self._lock:
            fetchid = self._availablefetchid()
            taskid = self._availabletaskid()
            task = self._base[taskid]
            self._fetched[fetchid] = taskid
            return (fetchid, task)
    
    def _availabletaskid(self):
        for i in range(len(self._base)):
            if not self._istaskfetched(i):
                return i
        raise NoTask
    
    def _availablefetchid(self):
        for j in range(len(self._fetched)):
            if j not in self._fetched:
                return j
        return len(self._fetched)
    
    def _istaskfetched(self, taskid):
        return taskid in self._fetched.values()
    
    def feedback(self, fetchid, result = True):
        with self._lock:
            taskid = self._fetched[fetchid]
            del self._fetched[fetchid]
            if result:
                self._removetask(taskid)
    
    def _removetask(self, taskid):
        del self._base[taskid]
        for e in self._fetched:
            if self._fetched[e] >= taskid:
                self._fetched[e] -= 1

class diskqueue:
    def __init__(self, file):
        self._file = file
        self._lock = threading.Lock()
        if os.path.isfile(file):
            with open(file, 'rb') as f:
                self._queue = pickle.load(f)
        else:
            self._queue = []
            self._save()
    
    def empty(self):
        with self._lock:
            return self._queue == []
    
    def append(self, x):
        with self._lock:
            self._queue.append(x)
            self._save()
    
    def __len__(self):
        with self._lock:
            return len(self._queue)
    
    def __getitem__(self, x):
        with self._lock:
            return self._queue[x]
    
    def __delitem__(self, x):
        with self._lock:
            del self._queue[x]
            self._save()
    
    def _save(self):
        dir = os.path.dirname(self._file)
        if not os.path.exists(dir):
            os.makedirs(dir)
        with open(self._file, 'wb') as f:
            pickle.dump(self._queue, f)

import time, random
from threading import Thread

def testmain():
    q = taskqueue(diskqueue('D:\\testqueue'))
    def handlethread():
        while True:
            try:
                taskid, name = q.fetchtask()
                print('start', name)
                time.sleep(random.randrange(1000)/1000)
                if random.choice([True, True]):
                    q.feedback(taskid, True)
                    print('ok', name)
                else:
                    q.feedback(taskid, False)
                    print('fail', name)
            except NoTask:
                pass
            time.sleep(0.1)
    def taskthread():
        for i in range(1000):
            x = random.randrange(10)
            print('supply', x)
            q.append(x)
            #print('new', i)
            time.sleep(0.1)
            #time.sleep(random.randrange(1000)/1000*len(q)/100)
    for i in range(10):
        Thread(target = handlethread).start()
    for i in range(1):
        Thread(target = taskthread).start()
    taskthread()

if __name__ == '__main__':
    testmain()