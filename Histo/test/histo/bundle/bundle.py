import logging as logger

def testBundle(bundle, threadCount=10, actionCount=9999999999999999, fileSize=1024*1024, extraActions=[]):
    fileNames = FileNames()
    for _ in range(threadCount):
        TestThread(bundle, actionCount, fileNames, fileSize, extraActions).start()

from threading import Thread
class TestThread(Thread):
    def __init__(self, bundle, actionCount, fileNames, fileSize, extraActions):
        Thread.__init__(self)
        self.bundle = bundle
        self.actionCount = actionCount
        self.fileNames = fileNames
        self.fileSize = fileSize
        self.extraActions = extraActions
        self.files = []
        
    def run(self):
        for _ in range(self.actionCount):
            try:
                self.randomAction()
            except Exception as e:
                logger.exception(e)
    
    def randomAction(self):
        actions = [self.testWrite, self.testRead, self.testList] + self.extraActions
        import random
        random.choice(actions)()
    
    def testWrite(self):
        logger.debug('[ Test write')
        logger.debug('[ Get file name')
        file = next(self.fileNames)
        logger.debug(' ]%s' % file)
        logger.debug('[ Open file')
        with self.bundle.open(file, 'wb') as f:
            logger.debug(' ]')
            logger.debug('[ Generate file data')
            data = self.FileData(file)
            logger.debug(' ]')
            logger.debug('[ Write file')
            writeAll(data, f)
            logger.debug(' ]')
            logger.debug('[ Close file')
        logger.debug(' ]')
        logger.debug('[ Append file list')
        self.files.append(file)
        logger.debug(' ]')
        logger.debug(' ]')
    
    def testRead(self):
        logger.debug('[ Test read')
        if not self.files:
            logger.debug('No file to read')
            return
        logger.debug('[ Get file name')
        file = self.randomFile()
        logger.debug(' ]%s' % file)
        logger.debug('[ Open file')
        with self.bundle.open(file, 'rb') as f:
            logger.debug(' ]')
            logger.debug('[ Read file')
            read = readAll(f)
            logger.debug(' ] length = %d' % len(read))
            logger.debug('[ Check read result')
            assert self.FileData(file) == read
            logger.debug(' ]')
            logger.debug('[ Close file')
        logger.debug(' ]')
        logger.debug(' ]')
    
    def testList(self):
        logger.debug('[ Test list')
        logger.debug('[ List')
        result = self.bundle.list()
        logger.debug(' ] length = %s' % len(result))
        logger.debug(' ]')
    
    def testDelete(self):
        logger.debug('[ Test delete')
        if not self.files:
            logger.debug('No file to delete')
            return
        logger.debug('[ Get file name')
        file = self.randomFile()
        logger.debug(' ]%s' % file)
        logger.debug('[ Delete')
        self.bundle.delete(file)
        logger.debug(' ]')
        logger.debug(' ]')
    
    def randomFile(self):
        import random
        return random.choice(self.files)
    
    def FileData(self, file):
        from random import Random
        r = Random(file)
        length = abs(int(r.gauss(self.fileSize, self.fileSize/3)))
        return bytes([r.randrange(256) for _ in range(length)])

def FileNames():
    from itertools import count
    from hashlib import md5
    for i in count():
        yield '%04d-' % i + md5(bytes(str(i),'utf8')).hexdigest()[:8]

def readAll(file):
    result = bytearray()
    for e in GaussReader(file, 10000, 3000):
        logger.debug('Read part, length=%d' % len(e))
        result.extend(e)
    return bytes(result)

def writeAll(data, file):
    from io import BytesIO
    for e in GaussReader(BytesIO(data), 10000, 3000):
        logger.debug('[ Write data, length=%d' % len(e))
        file.write(e)
        logger.debug(' ]')

def GaussReader(file, mean, sigma):
    for e in PositiveGaussSequence(mean, sigma):
        read = file.read(e)
        if not read:
            break
        yield read

def PositiveGaussSequence(mean, sigma):
    import random
    while True:
        yield int(abs(random.gauss(mean, sigma)))+1