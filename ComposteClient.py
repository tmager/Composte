#!/usr/bin/env python3

from network.client import Client as NetworkClient
from network.fake.security import Encryption
from network.base.loggable import DevNull, StdErr

from protocol import client, server
from util import misc
from threading import Thread, Lock

import json

class ComposteClient:
    def __init__(self, interactive_remote, broadcast_remote, broadcast_handler
            logger, encryption_scheme):
        """
        RPC host for connecting to Composte Servers. Connects to a server
        listening at interactive_remote and broadcasting on on
        broadcast_remote. Logs are directed to logger, and messages are
        transpatransparently encrypted and encrypted with
        encryption_scheme.encrypt() and decrypted with
        encryption_scheme.decrypt().
        Broadcasts are handled with broadcast_handler
        """

        self.__client = NetworkClient(interactive_remote, broadcast_remote,
                logger, encryption_scheme)
        self.__client.start_background(broadcast_handler)

        self.__client.info("Connecting to {} and {}".format(
            interactive_remote, broadcast_remote
        ))

        self.__version_handshake()

    def __version_handshake(self):
        """
        Perform a version handshake with the remote Composte server
        """
        msg = client.serialize("handshake", misc.get_version())
        reply = self.__client.send(msg)
        print(reply)

    def register(self, uname, pword, email):
        """
        Attempt to register a new user
        """
        msg = client.serialize("register", uname, pword, email)
        reply = self.__client.send(msg)
        print(reply)

    # We probably need cookies for login too, otherwise people can request
    # project listings (and thus projects) and subscribe to projects they
    # shouldn't be able to. This isn't an issue for the minimum deliverable
    # for the course, but it is an issue in the long run
    def login(self, uname, pword):
        """
        Attempt to login as a user
        """
        msg = client.serialize("login", uname, pword)
        reply = self.__client.send(msg)
        # status, reason = reply
        print(reply)

    def create_project(self, uname, pname, metadata):
        """
        Attempt to create a project
        """
        metadata["owner"] = uname
        metadata = json.dumps(metadata)
        msg = client.serialize("create_project", uname, pname, metadata)
        reply = self.__client.send(msg)
        print(reply)

    def retrieve_project_listings_for(self, uname):
        """
        Get a list of all projects this user is a collaborator on
        """
        msg = client.serialize("list_projects", uname)
        reply = self.__client.send(msg)
        reply = server.deserialize(reply)
        if reply[0] == "ok":
            return reply[1]
        else: return None

    def get_project(self, pid):
        """
        Get a project to work on
        """
        msg = client.serialize("get_project", pid)
        reply = self.__client.send(msg)
        print(reply)

    # Realistically, we send a login cookie and the server determines the user
    # from that, but we don't have that yet
    def subscribe(self, uname, pid):
        """
        Subscribe to updates to a project
        """
        msg = client.serialize("subscribe", uname, pid)
        reply = self.__client.send(msg)
        # print(reply)
        j = json.loads(reply)
        print(j[1][0])
        return j[1][0]

    def unsubscribe(self, cookie):
        """
        Unsubscribe to updates to a project
        """
        msg = client.serialize("unsubscribe", cookie)
        reply = self.__client.send(msg)
        print(reply)

    # There's nothing here yet b/c we don't know what anything look like
    def update(self, *args):
        """
        Send a music related update for the remote backend to process
        """
        print("Update with args: {}".format(str(args)))
        msg = client.serialize("update")
        reply = self.__client.send(msg)
        print(reply)

    def changeKeySignature(self, offset, partIndex, newSigSharps):
        return self.update("changeKeySignature", offset, partIndex,
                newSigSharps)

    def insertNote(self, offset, partIndex, pitch, duration):
        return self.update("insertNote", offset, partIndex, pitch, duration)

    def removeNote(self, offset, partIndex, removedNoteName):
        return self.update("removeNote", offset, partIndex, removedNoteName)

    def insertMetronomeMark(self, offset, parts, text, bpm, pulseDuration):
        return self.update("inertMetronomeMark", offset, parts, text, bpm,
                pulseDuration)

    def removeMetronomeMark(self, offset, parts):
        return self.update("removeMetronomeMark", offset, parts)

    def transpose(self, partIndex, semitones):
        reteurn self.update("transpose", partIndex, semitones)

    def insertClef(self, offset, part, clefStr):
        return self.update("insertClef", offset, part, clefStr)

    def removeClef(self, offset, part):
        return self.update("removeClef", offset, part)

    def insertMeasures(self, insertionOffset, parts, insertedQLs):
        return self.update("insertMeasures", insertionOffset, parts,
                insertedQLs)

    def addInstrument(self, offset, part, instrumentStr):
        return self.update("addInstrument", offset, part, instrumentStr)

    def removeInstrument(self, offset, part):
        return self.update("removeInstrument", offset, part)

    def addDynamic(self, offset, part, dynamicStr):
        return self.update("addDynamic", offset, part, dynamicStr)

    def removeDynamic(self, offset, part):
        return self.update("removeDynamic", offset, part)

    def addLyric(self, offset, part, lyric):
        return self.update("addLyric", offset, part, lyric)

    def stop(self):
        """
        Stop the client elegantly
        """
        self.__client.stop()

if __name__ == "__main__":
    import sys

    from network import dns

    import argparse

    parser = argparse.ArgumentParser(prog = "ComposteServer",
            description = "A Composte Server")

    parser.add_argument("-i", "--interactive-port", default = 5000,
            type = int)
    parser.add_argument("-b", "--broadcast-port", default = 5001,
            type = int)
    parser.add_argument("-r", "--remote-address", default = "composte.me",
            type = str)

    args = parser.parse_args()

    endpoint_addr = args.remote_address
    iport = args.interactive_port
    bport = args.broadcast_port

    c = ComposteClient("tcp://{}:{}".format(endpoint_addr, iport),
            "tcp://{}:{}".format(endpoint_addr, bport),
            StdErr, Encryption())

    c.register("msheldon", "A", "!!!")

    # sys.exit(0)

    c.register("shark meldon", "A", "!!!")
    c.register("mark", "A", "!!!")
    c.register("a", "A", "!!!")
    c.login("msheldon", "A")
    c.login("msheldon", "B")

    print(json.dumps({"owner": "msheldon"}))
    c.create_project("msheldon", "a_project", {"owner": "msheldon"})

    # sys.exit(0)

    [a_pid] = c.retrieve_project_listings_for("msheldon")
    c.retrieve_project_listings_for("alex")

    # print(type(a_pid))
    # print(a_pid)
    proj = json.loads(a_pid)[0]
    print(proj)

    pid = json.loads(proj)["id"]
    print(pid)

    c.get_project(pid)

    cookie = c.subscribe("msheldon", pid)
    c.subscribe("shark meldon", pid)

    c.unsubscribe(cookie)
    c.unsubscribe("not a cookie")

    # c.update("AAAAAAAAAAAAAAA")

    c.stop()

