import struct

def _packint(a):
    return struct.pack('!i',a)

def _packlong(a):
    return struct.pack('!q',a)

def _unpackint(a):
    return struct.unpack('!i', a)[0]

def _unpacklong(a):
    return struct.unpack('!q', a)[0]

class datastream:
    def __init__(self, stream):
        self._stream = stream
    
    def write(self, data):
        self._stream.write(data)
    
    def writeint(self, a):
        self.write(_packint(a))
    
    def writelong(self, a):
        self.write(_packlong(a))
    
    def writebytes(self, a):
        self.writeint(len(a))
        self.write(a)
    
    def read(self, limit = None):
        return self._stream.read(limit)
    
    def readint(self):
        return _unpackint(self.read(4))
    
    def readlong(self):
        return _unpacklong(self.read(8))
    
    def readbytes(self):
        length = self.readint()
        result = self._stream.read(length)
        assert len(result) == length
        return result
    
class objectstream:
    def __init__(self, stream):
        self._stream = stream
        
    def write(self, data):
        self._stream.write(data)
    
    def read(self, limit = None):
        return self._stream.read(None)
    
    def writeobject(self, object):
        import pickle
        pickle.