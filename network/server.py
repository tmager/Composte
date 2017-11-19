#!/usr/bin/env python3

import zmq
# A REP socket replies to the client who sent the last message. This means
# that we can't really get away with worker threads here, as
# REQ/Processing/REP must be serialized as a cohesive unit.

from threading import Lock

from fake.security import Encryption, Log
from base.exceptions import DecryptError, EncryptError, GenericError

from base.loggable import Loggable

from conf import logging as log
import logging

# Need signal handlers to properly run as daemon
import signal
import sys
import traceback

DEBUG = True

# Broadcast socket   -> Publish/Subscribe
# Interactive socket -> Request/Reply
class Server(Loggable):
    __context = zmq.Context()
    def __init__(self, interactive_address, broadcast_address,
            logger, encryption_scheme = Encryption()):
        """
        Server.__init__(self, interactive_address, broadcast_address,
            logger, encryption_scheme = Encryption(), logger = None)
        The network server for Composte.
        interactive_address and broadcast_address must be available for this
        application to bind to.
        encryption_scheme must provide encrypt and decrypt methods
        logger must support at least the methods of base.loggable.Loggable
        """
        super(Server, self).__init__(logger)

        self.__translator = encryption_scheme

        self.__iaddr = interactive_address
        self.__isocket = self.__context.socket(zmq.REP)
        self.__isocket.bind(self.__iaddr)

        self.__baddr = broadcast_address
        self.__bsocket = self.__context.socket(zmq.PUB)
        self.__bsocket.bind(self.__baddr)

        self.__done = False

        self.__ilock = Lock()
        self.__block = Lock();

        # print("Bound to {} and {}".format(self.__iaddr, self.__baddr))

    def broadcast(self, message):
        """
        Server.broadcast(self, message)
        Broadcast a message to all subscribed clients
        """
        self.info("Broadcasting {}".format(message))
        with self.__block:
            self.__bsocket.send_string(message)

    def fail(self, message, reason):
        """
        Server.fail(self, message, reason)
        Send a failure message to a client
        """
        with self.__ilock:
            # Probably need a better generic failure message format, but eh
            self.error("Failure ({}): {}".format(message, reason))
            self.__isocket.send_string("Failure ({}): {}".format(reason,
                message))

    def listen_almost_forever(self, handler = lambda x: x,
            preprocess = lambda x: x, postprocess = lambda msg: msg,
            poll_timeout = 2000):
        """
        Server.listen_almost_forever(self, handler = lambda msg: msg,
            preprocess = lambda msg: msg, poll_timeout = 2000)
        Polls for messages on the interactive socket until the server is
        stopped. poll_timeout controls how long a poll operation will wait
        before failing.
        Messages are pushed through the pipeline preprocess -> handler ->
        postprocess, and the result is sent back to as a client
        """
        try:
            while True:
                with self.__ilock:
                    if self.__done: break

                    nmsg = self.__isocket.poll(poll_timeout)
                    if nmsg == 0:
                        continue
                    message =  self.__isocket.recv_string()
                    # Unconditionally catch and ignore _all_ unexpected
                    # exceptions during the invocations of client-provided
                    # functions
                    try:
                        try:
                            message = self.__translator.decrypt(message)
                        except DecryptError as e:
                            self.fail(message, "Decrypt failure")
                            continue

                        try:
                            message = preprocess(message)
                        except GenericError as e:
                            self.fail(message, "Internal server error")
                            continue

                        try:
                            reply = handler(self, message)
                        except GenericError as e:
                            self.fail(message, "Internal server error")
                            continue

                        try:
                            reply = postprocess(reply)
                        except GenericError as e:
                            self.fail(message, "Internal server error")
                            continue

                        try:
                            reply = self.__translator.encrypt(reply)
                        except EncryptError as e:
                            self.fail(message, "encrypt failure")
                            continue
                    except:
                        self.error("Uncaught exception: {}"
                                .format(traceback.format_exec()))
                        continue

                    self.__isocket.send_string(reply)
        except KeyboardInterrupt as e:
            self.stop()
            print()

    def stop(self):
        """
        Server.stop(self)
        Stop the server
        """
        self.info("Shutting down server")
        with self.__ilock:
            self.__done = True
            self.__isocket.unbind(self.__iaddr)

        with self.__block:
            self.__bsocket.unbind(self.__baddr)

def echo(server, message):
    """
    Echo the message back to the client
    """
    server.info("Echoing {}".format(message))
    server.broadcast(message)
    return message

def stop_server(sig, frame, server):
    server.stop()

if __name__ == "__main__":

    if not DEBUG:
        signal.signal(signal.SIGINT , lambda sig, f: stop_server(sig, f, s))
        signal.signal(signal.SIGQUIT, lambda sig, f: stop_server(sig, f, s))
        signal.signal(signal.SIGTERM, lambda sig, f: stop_server(sig, f, s))
        signal.signal(signal.SIGSTOP, lambda sig, f: stop_server(sig, f, s))

    log.setup()

    logging.getLogger(__name__).info("Hello yes this is a test")

    # Set up the server
    s = Server("ipc:///tmp/interactive", "ipc:///tmp/broadcast",
            logging.getLogger("server"), Log(sys.stderr))

    # Start listening
    s.listen_almost_forever(echo)

