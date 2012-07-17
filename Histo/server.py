from stream import copy, objectstream
from summary import generatesummary
from netserver import netserver
from timetuple import nowtuple
from autotemp import tempdir
from repo import repo
from datetime import datetime
from taskqueue import diskqueue,taskqueue, NoTask
from filelock import filelock
from threading import Thread
import hashlib, pchex, threading, summary
import pickle, time, smtp, os, io, sys, logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='[%Y-%m%d %H:%M:%S]')

usage = """\
server root key
"""

def run(root, key):
    print(usage)
    smtp = smtpserver(root)
    queue = smtp.getqueue()
    logging.debug('Starting main server')
    main = mainserver(repo(root, key, queue))
    main.start()
    logging.debug('Starting smtp service')
    smtp.start()
    logging.debug('Service running')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    smtp.shutdown()
    main.shutdown()

class sendthread(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self._queue = queue
        self._exit = False
    
    def shutdown(self):
        self._exit = True
    
    def run(self):
        while not self._exit:
            time.sleep(1)
            try:
                taskid, each = self._queue.fetchtask()
            except NoTask:
                continue
            path = each[0]
            name = os.path.basename(path)
            with filelock(path):
                lastmodify = os.path.getmtime(path)
                with open(path, 'rb') as f:
                    data = f.read()
            lastmodify = datetime.fromtimestamp(lastmodify)
            lastmodify = '{:06d}-{:02d}{:02d}{:02d}-{:02d}{:02d}-{:04d}'.format(*reversed(list(lastmodify.timetuple())))
            hash = pchex.encode(hashlib.new('md5', data).digest())
            sender = 'histo@caipeichao.com'
            receiver = each[1]
            subject = name
            content = '%s-%s' % (lastmodify, hash)
            attachmentname = name
            attachmentdata = data
            logging.debug('sending {} to {}'.format(name, receiver))
            try:
                smtp.sendmail(sender, receiver, subject, content, attachmentname, attachmentdata)
            except Exception as e:
                self._queue.feedback(taskid, False)
                logging.exception(e)
            else:
                self._queue.feedback(taskid, True)
            logging.debug('finish send {}'.format(name))

class smtpserver:
    def __init__(self, root):
        self._queue = taskqueue(diskqueue(os.path.join(root, 'sendqueue')))
    
    def getqueue(self):
        return self._queue
    
    def shutdown(self):
        for e in self._threads:
            e.shutdown()
    
    def start(self):
        threadcount = 5
        self._threads = [sendthread(self._queue) for i in range(threadcount)]
        for e in self._threads:
            e.start()

def loadindex(repo):
    try:
        f = repo.open('index', 'rb')
    except IOError:
        return []
    missing = f.getmissingparts()
    if missing:
        raise Exception('Missing parts: ' + ' '.join(missing))
    stream = f.read()
    f.close()
    stream = objectstream(io.BytesIO(stream))
    result = []
    while True:
        try:
            result.append(indexitem(stream.readobject()))
        except EOFError:
            break
    return result

def indexitem(x):
    return dict(x)

class mainserver(netserver):
    def __init__(self, repo):
        netserver.__init__(self, ('0.0.0.0', 13750), self.handle)
        self._index = loadindex(repo)
        self._commit = commit(repo, self._index)
        self._search = search(self._index)
        self._get = get(repo)
        self._lock = threading.Lock()
    
    def handle(self, stream):
        method = stream.readobject()
        logging.debug('request: ' + method)
        t = {'commit': self._commit.run,
             'search': self._search.run,
             'get': self._get.run}
        with self._lock: #WARNING: Careful remove the lock. Thinking about multithread situation
            t[method](stream)

class commit:
    def __init__(self, repo, index):
        self._repo = repo
        self._index = index
        
    def run(self, stream):
        datetime = stream.readobject()
        if datetime == None:
            datetime = nowtuple()
        name = stream.readobject()
        lastmodify = stream.readobject()
        filename = stream.readobject()
        filesize = stream.readobject()
        logging.debug('name: ' + name)
        logging.debug('filesize: {}'.format(filesize))
        logging.debug('receiving data')
        with tempdir('histo-repo-') as t:
            temp = os.path.join(t, filename)
            with open(temp, 'wb') as f:
                assert copy(stream, f, filesize) == filesize
            logging.debug('receive data ok')
            logging.debug('writting to repo')
            datafile = self._repo.open('data', 'wb')
            start = datafile.tell()
            with open(temp, 'rb') as f:
                copy(f, datafile, filesize)
            end = datafile.tell()
            summary = generatesummary(name, temp, depthlimit = 1)
            index = (('datetime', datetime),
                     ('name', name),
                     ('last-modify', lastmodify),
                     ('range', (start, end)),
                     ('summary', summary))
            indexfile = self._repo.open('index', 'wb')
            objectstream(indexfile).writeobject(index)
            datafile.close()
            indexfile.close()
            logging.debug('write ok')
        self._index.append(indexitem(index))
        stream.writeobject('ok')
        logging.debug('all ok')

class search:
    def __init__(self, index):
        self._index = index
    
    def run(self, stream):
        keyword = stream.readobject()
        result = []
        for e in self._index:
            for e2 in summary.walk(e['summary']):
                if e2.find(keyword) >= 0:
                    result.append(e)
                    break
        stream.writeobject(result)

class get:
    def __init__(self, repo):
        self._repo = repo
    
    def run(self, stream):
        range = stream.readobject()
        f = self._repo.open('data', 'rb')
        f.seek(range[0])
        copy(f, stream, range[1] - range[0])
        f.close()

if __name__ == '__main__':
    run(sys.argv[1], pchex.decode(sys.argv[2]))