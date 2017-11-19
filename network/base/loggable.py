
from . import exceptions

import logging

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

# Ad-Hoc logger for and Loggable. Provide your own sink that supports
# write(). Usually an open file or sys.stderr.
# Does not do formatting, etc
class AdHoc:
    def __init__(self, sink, loglevel = 0, name = None, **kwargs):
        """
        Use kwargs to provide prefixes for loglevels:
            INFO
            DEBUG
            WARNING
            ERROR
            CRITICAL
        Prefixes default to the names of the loglevels
        The logger name is provided alongside all message
        """
        self.__sink = sink
        self.__level = loglevel
        self.__name = "{}/".format(name) if name else ""

        self.__prefixes = {
                "info": "[{}INFO]: ".format(self.__name),
                "debug": "[{}DEBUG]: ".format(self.__name),
                "warning": "[{}WARNING]: ".format(self.__name),
                "error": "[{}ERROR]: ".format(self.__name),
                "critical": "[{}CRITICAL]: ".format(self.__name),
        }
        self.__prefixes.update(kwargs)

    def __log(self, message, level):
        if self.__level >= level:
            self.__sink.write(message + "\n")

    def info(self, message):
        self.__log(self.__prefixes["info"] + message, logging.INFO)

    def debug(self, message):
        self.__log(self.__prefixes["debug"] + message, logging.DEBUG)

    def warn(self, message):
        self.__log(self.__prefixes["warn"] + message, logging.WARNING)

    def error(self, message):
        self.__log(self.__prefixes["error"] + message, logging.ERROR)

    def critical(self, message):
        self.__log(self.__prefixes["critical"] + message, logging.CRITICAL)

# Combine loggers
class Combined:
    def __init__(self, loggers):
        self.__loggers = []

        if type(loggers) == list:
            self.__loggers = loggers
        else: self.__loggers.append(loggers)

    def add(self, logger):
        self.__logger.append(logger)

    def remove(self, logger):
        try:
            self.__loggers.remove(logger)
        except ValueError: pass

    def info(self, message):
        for logger in self.__loggers:
            logger.info(message)

    def debug(self, message):
        for logger in self.__loggers:
            logger.debug(message)

    def warn(self, message):
        for logger in self.__loggers:
            logger.warn(message)

    def error(self, message):
        for logger in self.__loggers:
            logger.error(message)

    def critical(self, message):
        for logger in self.__loggers:
            logger.critical(message)

