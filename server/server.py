#!/usr/bin/env python3

import zmq
import sys

from fake.encryption import Encryption, Log

# Broadcast socket   -> Publish/Subscribe
# Interactive socket -> Request/Reply
class Server:
    __context = zmq.Context()
    def __init__(self, interactive_address, broadcast_address,
            encryption_scheme = Encryption()):

        self.__translator = encryption_scheme

        self.__iaddr = interactive_address
        self.__baddr = broadcast_address
        self.__isocket = self.__context.socket(zmq.REP)
        self.__bsocket = self.__context.socket(zmq.PUB)

        self.__isocket.bind(self.__iaddr)
        self.__bsocket.bind(self.__baddr)
        print("Bound to {} and {}".format(self.__iaddr, self.__baddr))

    def broadcast(self, message):
        self.__bsocket.send_string(str(message))

    def fail(self, message, reason):
        # Probably need a better generic failure message format, but eh
        self.__isocket.send_string("Failure ({}): {}".format(reason,
            str(message)))

    def listen_forever(self, handler = lambda x: x):
        try:
            while True:
                message =  self.__isocket.recv()
                print("Received {}".format(message))
                try:
                    message = self.__translator.decrypt(message)
                except DecryptError as e:
                    self.fail(message, "Decrypt failure")
                    continue

                try:
                    reply = handler(self, message)
                except GenericFailure as e:
                    self.fail(message, "Internal server error")
                    continue

                try:
                    reply = self.__translator.encrypt(message)
                except EncryptError as e:
                    self.fail(message, "encrypt failure")
                    continue

                self.__isocket.send_string(str(reply))
        except KeyboardInterrupt as e:
            pass

def echo(server, message):
    server.broadcast(message)
    return message

if __name__ == "__main__":
    print("WTFWD")

    s = Server("ipc:///tmp/interactive", "ipc:///tmp/broadcast", Log(sys.stderr))
    s.listen_forever(echo)

