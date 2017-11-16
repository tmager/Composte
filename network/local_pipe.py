# local_pipe.py
# Abstract away zmq push/pull mechanics.

# The PUSH end
class In:
    __context = zmq.Context()
    def __init__(self, address, preproccess = lambda x: x):
        self.__address = address
        self.__socket = self.__context.Socket(zmq.PUSH)
        self.__preprocess = preproccess

        self.__socket.bind(self.__address)

    def push(self, thing):
        self.__socket.send(self.__preprocess(thing))

# The PULL end
class Out:
    __context = zmq.Context()
    def __init__(self, address, preprocess = lambda x: x):
        self.__address = address
        self.__socket = self.__context.Socket(zmq.PULL)
        self.__preprocess = preprocess

        self.__socket.bind(self.__address)

    def recv(self):
        message = self.__preprocess(self.__socket.recv())
        return message

