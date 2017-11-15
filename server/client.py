#!/usr/bin/env python3

import zmq
from threading import Thread

from fake.encryption import Encryption, Log

# Likely need to have separate clients: one to handle client-server
# interactions and one to receive broadcasts

import sys

class Subscribe:
    def __init__(self, remote_address, zmq_context, encryption_scheme = Encryption()):
        self.__context = zmq_context
        self.__translator = encryption_scheme

        # Subscribe to remote broadcasts
        self.__addr = remote_address
        self.__socket = self.__context.socket(zmq.SUB)
        self.__socket.connect(self.__addr)
        print("Subscribed to {}".format(self.__addr))

    def recv(self):
        msg = self.__socket.recv()
        try:
            msg = self.__translator.decrypt(msg)
        except DecryptError as e:
            # log?
            raise e
        return msg

# Broadcast handler is separate: Subscribe. Should probably stick it in a
# thread off to the side.
class Client:
    __context = zmq.Context()
    def __init__(self, remote_address, broadcast_address,
            encryption_scheme = Encryption()):
        self.__translator = encryption_scheme

        # Interact with remote server
        self.__raddr = remote_address
        self.__isocket = self.__context.socket(zmq.REQ)
        self.__isocket.connect(self.__raddr)
        print("Connected to {}".format(self.__raddr))

        self.__listener = Subscribe(broadcast_address, self.__context,
                self.__translator)

        self.__background_thread = None

    def send(self, message):
        print("Sending {}".format(message))
        try:
            message = self.__translator.encrypt(message)
        except EncryptError as e:
            # log?
            raise e

        self.__isocket.send_string(str(message))
        msg = self.__isocket.recv()
        print("Received {}".format(msg))
        return msg

    def __listen_forever(self, handler):
        while True:
            try:
                msg = self.__listener.recv()
            except DecryptError as e:
                #log?
                continue
            handler(self, message)

    # No way to forcefuly stop threads in python, but partial clientside
    # updates on program termination don't matter at all, so we can just let
    # the thread die with the process.
    # This may point to processes being a better option
    def start_background_thread(self, handler):
        if self.__background_thread != None:
            return

        self.__background_thread = \
        Thread(target = self.__listen_forever,
                args = (handler,))

        self.__background_thread.start()

def echo(server, message):
    print("Received {}".format(message))
    return message

if __name__ == "__main__":
    s = Client("ipc:///tmp/interactive", "ipc:///tmp/broadcast", Log(sys.stderr))
    # s.start_background_thread(echo)

    s.send("Hello there")

    print("AAAAAAAAAAAAAAAA")
    sys.exit(0)

