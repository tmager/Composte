#!/usr/bin/env python3

from network.client import Client as NetworkClient
from network.fake.security import Encryption
from network.base.loggable import DevNull, StdErr

from protocol import client, server

from threading import Thread, Lock

import json

def get_version():
    import git

    try:
        return git.Repo(search_parent_directories = True).head.object.hexsha
    except git.exc.InvalidGitRepositoryError as e:
        return None

class ComposteClient:
    def __init__(self, interactive_remote, broadcast_remote,
            logger, encryption_scheme):

        self.__client = NetworkClient(interactive_remote, broadcast_remote,
                logger, encryption_scheme)
        self.__client.start_background(self.__handle_broadcast)

        self.__version_handshake()

    def __handle_broadcast(self, _, broadcast):
        print("Broadcast received: " + str(broadcast))

    def __version_handshake(self):
        msg = client.serialize(None, None, "handshake", get_version())
        reply = self.__client.send(msg)
        print(reply)

    def register(self, uname, pword, email):
        msg = client.serialize(uname, None, "register", pword, email)
        reply = self.__client.send(msg)
        print(reply)
        # (status, reason) = self.__client.send(msg)
        # print(status, reason)

    # We probably need cookies for login too, otherwise people can request
    # project listings (and thus projects) and subscribe to projects they
    # shouldn't be able to. This isn't an issue for the minimum deliverable
    # for the course, but it is an issue in the long run
    def login(self, uname, pword):
        msg = client.serialize(uname, None, "login", pword)
        reply = self.__client.send(msg)
        # status, reason = reply
        print(reply)

    def create_project(self, uname, pname):
        msg = client.serialize(uname, None, "create_project", pname)
        reply = self.__client.send(msg)
        print(reply)

    def retrieve_project_listings_for(self, uname):
        msg = client.serialize(uname, None, "list_projects")
        reply = self.__client.send(msg)
        reply = server.deserialize(reply)
        if reply[0] == "ok":
            return reply[1]
        else: return None

    def get_project(self, pid):
        msg = client.serialize(None, pid, "get_project")
        reply = self.__client.send(msg)
        print(reply)

    # Realistically, we send a login cookie and the server determines the user
    # from that, but we don't have that yet
    def subscribe(self, uname, pid):
        msg = client.serialize(uname, pid, "subscribe")
        reply = self.__client.send(msg)
        # print(reply)
        j = json.loads(reply)
        print(j[1][0])
        return j[1][0]

    def unsubscribe(self, cookie):
        msg = client.serialize(None, None, "unsubscribe", cookie)
        reply = self.__client.send(msg)
        print(reply)

    def update(self, *args):
        print("Update with args: {}".format(str(args)))
        msg = client.serialize(None, None, "update")
        reply = self.__client.send(msg)
        print(reply)

    def stop(self):
        self.__client.stop()

if __name__ == "__main__":
    import sys

    c = ComposteClient("tcp://127.0.0.1:6666", "tcp://127.0.0.1:6667",
            StdErr, Encryption())

    c.register("msheldon", "A", "!!!")

    # sys.exit(0)

    c.register("shark meldon", "A", "!!!")
    c.register("mark", "A", "!!!")
    c.register("a", "A", "!!!")
    c.login("msheldon", "A")
    c.login("msheldon", "B")

    c.create_project("msheldon", "a_project")

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

    c.update("AAAAAAAAAAAAAAA")

    c.stop()

