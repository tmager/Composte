
from . import exceptions

class IsNone(exceptions.GenericError): pass

class Loggable:
    def __init__(self, logger):
        if logger == None:
            raise IsNone("Logger must not be None")
        self.__logger = logger

    def info    (self, message): self.__logger.info    (message)
    def debug   (self, message): self.__logger.debug   (message)
    def warn    (self, message): self.__logger.warn    (message)
    def error   (self, message): self.__logger.error   (message)
    def critical(self, message): self.__logger.critical(message)

class devnull(Loggable):
    def __init__(self, logger = None): pass

    def info    (self, message): pass
    def debug   (self, message): pass
    def warn    (self, message): pass
    def error   (self, message): pass
    def critical(self, message): pass

DevNull = devnull()

