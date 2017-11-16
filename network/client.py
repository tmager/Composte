#!/usr/bin/env python3

import zmq
from threading import Thread, Lock
from queue import Queue

from fake.encryption import Encryption, Log
from fake.exceptions import EncryptError, DecryptError, GenericError

import sys

class Subscribe:
    def __init__(self, remote_address, zmq_context):
        """
        Subscribe.__init__(self, remote_address, zmq_context)
        Subscribe to a publishing endpoint at remote_address
        Requires a zmq context
        """

        self.__context = zmq_context

        # Subscribe to remote broadcasts
        self.__addr = remote_address
        self.__socket = self.__context.socket(zmq.SUB)
        self.__socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.__socket.connect(self.__addr)
        # print("Subscribed to {}".format(self.__addr))

        self.__backlog = Queue(1024)
        self.__lock = Lock()

    def recv(self):
        """
        Subscribe.recv(self)
        Retrieve a message, failing after a timeout.
        Returns string on success, None on failure
        """
        # If we have a backlog, deal with that first, in order
        with self.__lock:
            empty = self.__backlog.empty()

            if not empty:
                msg = self.__backlog.get()
            else:
                # Wait up to 500 ms
                nmsg = self.__socket.poll(500)
                if nmsg == 0:
                    msg = None
                    return msg
                for i in range(nmsg):
                    self.__backlog.put(self.__socket.recv_string())
                    msg = self.__backlog.get()

        return msg

    def stop(self):
        """
        Subscribe.stop(self)
        Stop listening for broadcasts
        """
        with self.__lock:
            self.__socket.disconnect(self.__addr)
            self.__socket.close()

# Broadcast handler is separate: Subscribe. Should probably stick it in a
# thread off to the side.
class Client:
    __context = zmq.Context()
    def __init__(self, remote_address, broadcast_address,
            encryption_scheme = Encryption()):
        """
        Client.__init__(self, remote_address, broadcast_address,
            encryption_scheme)
        Network client for Composte. Opens an interactive connection and a
        subscription to the server.
        encryption_scheme must provide encrypt and decrypt methods
        """
        self.__translator = encryption_scheme

        # Interact with remote server
        self.__raddr = remote_address
        self.__isocket = self.__context.socket(zmq.REQ)
        self.__isocket.connect(self.__raddr)

        # Receive broadcasts
        self.__done = False
        self.__background = None
        self.__listener = Subscribe(broadcast_address, self.__context)

        self.__lock = Lock()

    def send(self, message, preprocess = lambda x: x):
        """
        Client.send(self, message, preprocess = lambda msg: msg)
        Send a message down the interactive socket, blocking until a reply is
        received.
        The reply is fed through preprocess before being returned
        """
        with self.__lock:
            try:
                message = self.__translator.encrypt(message)
            except EncryptError as e:
                # log?
                raise e

            self.__isocket.send_string(message)
            msg = self.__isocket.recv_string()

            try:
                msg = preprocess(msg)
            except GenericError as e:
                # log?
                raise e
            return msg

    def __listen_almost_forever(self, handler, preprocess = lambda x: x):
        """
        Client.__listen_almost_forever(self, handler,
            preprocess = lambda msg: msg)
        Listen for messages until the client is stopped.
        Messages are pipelined through preprocess and then handler.
        """
        while True:
            # print("Listening for broadcasts")
            with self.__lock:
                if self.__done: break

            msg = self.__listener.recv()
            if msg == None:
                continue

            try:
                msg = self.__translator.decrypt(msg)
            except DecryptError as e:
                #log?
                continue

            try:
                msg = preprocess(msg)
            except GenericError as e:
                # log?
                continue

            try:
                handler(self, msg)
            except GenericError as e:
                # log?
                continue

        self.__listener.stop()

    def start_background(self, handler, preprocess = lambda x: x):
        """
        Client.start_background(self, handler, preprocess = lambda msg: msg)
        Hands off to Clinet.__listen_almost_forever
        Start thread listening for broadcasts from the remote Composte server
        Does nothing if the thread has already been started
        """
        with self.__lock:
            if self.__background != None:
                return

            self.__background = \
            Thread(target = self.__listen_almost_forever,
                    args = (handler, preprocess))

            self.__background.start()

    def stop(self):
        """
        Client.stop(self)
        Stop all network activity for this Composte client
        """
        with self.__lock:
            self.__isocket.disconnect(self.__raddr)
            self.__isocket.close()

            self.__done = True

        self.__background.join()
        self.__background = None

def echo(server, message):
    return message

def id(pre, elem):
    return pre + elem

if __name__ == "__main__":
    # Set up the servers
    s1 = Client("ipc:///tmp/interactive", "ipc:///tmp/broadcast",
            Encryption())
    s2 = Client("ipc:///tmp/interactive", "ipc:///tmp/broadcast",
            Encryption())

    # Start broadcast handlers
    s1.start_background(echo, lambda m: id("1: ", m))
    s2.start_background(echo, lambda m: id("2: ", m))

    # Poke the server
    for i in range(10):
        rep = s1.send("Hello there", lambda m: id("1: ", m))
        print("Reply: " + rep)

        rep = s2.send("Are you there?", lambda m: id("2: ", m))
        print("Reply: " + rep)

    # Stop the clients
    s1.stop()
    s2.stop()

