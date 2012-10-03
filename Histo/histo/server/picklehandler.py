import logging as logger

class PickleHandler:
    def __init__(self, config, state, index, dataBundle, stream):
        self.config = config
        self.state = state
        self.index = index
        self.dataBundle = dataBundle
        self.stream = stream
    
    def run(self):
        method = self.readMethod()
        self.handleRequest(method)
    
    def readMethod(self):
        logger.debug('[ Reading request')
        method = self.stream.readObject()
        logger.debug(' ]%s', method)
        return method
    
    def handleRequest(self, method):
        logger.debug('[ Handle request')
        config = self.config
        state = self.state
        index = self.index
        dataBundle = self.dataBundle
        stream = self.stream
        from histo.server.requesthandler import RequestHandler
        handler = RequestHandler(method, config, state, index, dataBundle, stream)
        result = handler.run()
        logger.debug(' ]%s', result)
