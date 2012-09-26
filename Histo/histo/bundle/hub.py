class Hub:
    def __init__(self, bundles, volumes, state):
        self.bundles = bundles
        self.volumes = volumes
        self.state = state
        
    def open(self, name, mode):
        if mode == 'rb':
            return self.openForRead(name)
        elif mode == 'wb':
            return self.openForWrite(name)
        else:
            raise Exception('No such mode.')
    
    def delete(self, name):
        raise Exception('Not supported')
    
    def list(self, name):
        result = set()
        for e in self.bundles:
            result = result.union(e.list())
        return list(result)
    
    def exists(self, name):
        return any((e.exists(name) for e in self.bundles))
    
    def openForRead(self, name):
        bundle = self.findContainerBundle(name)
        return bundle.open(name, 'rb')
    
    def openForWrite(self, name):
        import io
        result = io.BytesIO()
        def onClose(close0):
            close0()
            size = result.tell()
            bundle = self.findBigEnoughBundle(size)
            with bundle.open(name, 'wb') as f:
                f.write(result.getvalue())
        from .filehook import FileHook
        return FileHook(result, onClose=onClose)
    
    def findBigEnoughBundle(self, size):
        for i in range(len(self.bundles)):
            if self.getBundleRemainSize(i) >= size:
                return self.bundles[i]
        raise Exception('Space not enough')
    
    def getBundleRemainSize(self, i):
        totalSize = self.volumes[i]
        usedSize = self.state['Usage'][i]
        return totalSize - usedSize