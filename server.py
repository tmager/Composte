#!/usr/bin/env python3

# Things that should probably be a thing:
# * Centralized pool of projects in memory (Pretty critical, otherwise edits
#           don't survive)
#       Requires support for project deserialization
# * Timed flushing of projects in memory to disk (Important for robustness)
#       Requires support for project serialization
#       Likely requires projects to carry locks serverside to prevent writes
#           during a flush causing project corruption
# * Login cookies alongside project subscription cookies
# * Separation of broadcasts per project (regardless of encryption)
#       Would require moving from single broadcast to some other strategy

from network.server import Server as NetworkServer
from network.fake.security import Encryption
from network.base.loggable import DevNull, StdErr
from network.base.exceptions import GenericError

from protocol import client, server

from auth import auth
from database import driver

from util import musicWrapper, bookkeeping, composteProject, timer

from threading import Thread, Lock
import uuid
import json
import os
import sqlite3

# This is going to hurt
def get_version():
    import git
    try:
        return git.Repo(search_parent_directories = True).head.object.hexsha
    except git.exc.InvalidGitRepositoryError as e:
        return None

class ComposteServer:

    # I'm so sorry
    __register_lock = Lock()

    def __init__(self, interactive_address, broadcast_address,
            logger, encryption_scheme, data_root = "data/"):

        self.__server = NetworkServer(interactive_address, broadcast_address,
                logger, encryption_scheme)

        self.__server.start_background(self.__handle, self.__preprocess,
                self.__postprocess)

        self.__users        = None
        self.__projects     = None
        self.__contributors = None

        self.version = get_version()
        self.__data_root = data_root
        self.__project_root = os.path.join(self.__data_root, "users")

        # This is a dummy function
        self.__timer = timer.every(300, lambda: False)

        try:
            os.mkdir(self.__project_root)
        except FileExistsError as e:
            pass

        self.sessions = {}

    # Database interactions

    def register(self, uname, pword, email):
        hash_ = auth.hash(pword)

        with ComposteServer.__register_lock:
            hopefully_None = self.__users.get(uname)
            if hopefully_None.uname is not None:
                return ("fail", "Username is taken")

            # Apparently exceptions on writes cause the database to lock...
            try:
                self.__users.put(uname, hash_, email)
            except sqlite3.IntegrityError:
                return ("fail", "Username is taken")
            except sqlite3.DatabaseError as e:
                # raise e
                return ("fail", "Generic failure")

        try:
            os.mkdir(os.path.join(self.__project_root, uname))
        except FileExistsError as e:
            pass

        return ("ok", "")

    def login(self, uname, pword):
        record = self.__users.get(uname)
        if record.hash is None:
            return ("fail", "failed to login")

        success = auth.verify(pword, record.hash)
        if success:
            listings = self.__contributors.get_projects(uname)
            listings = [ str(project) for project in listings ]
            return ("ok", str(listings))
        else:
            return ("fail", "failed to login")

    def create_project(self, uname, pname):
        """
        TODO: Actually create a project, not just a database entry
        """
        # This is questionable, but okay
        proj = composteProject.ComposteProject(uname, { "title": pname })
        uuid = str(proj.projectID)
        try:
            self.__projects.put(uuid, pname, uname)
        except sqlite3.OperationalError as e:
            self.__server.info("?????????????")
            raise GenericError("The database is fucked")

        hopefully_not_None = self.__users.get(uname)
        if hopefully_not_None is None:
            return ("fail", "User {} is not registered".format(uname))

        # This could then potentially also lock the database...
        try:
            self.__contributors.put(uname, uuid)
        except sqlite3.IntegrityError as e:
            raise e
            return ("fail", "User {} is not registered".format(uname))

        base_path = os.path.join(self.__project_root, uname)
        base_path = os.path.join(base_path, uuid)
        with open(base_path + ".meta", "w") as f:
            f.write("Hello yes this is metadata for {}".format(uuid))

        with open(base_path + ".composte", "w") as f:
            f.write("Hello yes this is project {}".format(uuid))

        return ("ok", uuid)

    # This one is slightly more complicated
    def get_project(self, pid):
        """
        TODO: Actually read a project from disk, not just pretend to
        """
        project_entry = self.__projects.get(pid)
        if project_entry.id == None:
            return ("fail", "Project not found")

        pid = project_entry.id
        owner = project_entry.owner

        meta, proj = self.get_project_contents(owner, pid)

        # Do something here with bookkeeping.Pool, in the spirit of
        # proj = bookkeeping.Pool.get(pid, get_project_contents(owner, pid))
        # Deserialization wil be required, since we must distinguish between
        # serialized forms for transfer and object forms for manipulation

        return ("ok", (meta, proj))

    # TODO: This can probably fail
    def list_projects_by_user(self, uname):
        listings = self.__contributors.get(username = uname)
        listings = [ str(project) for project in listings ]
        return ("ok", json.dumps(listings))

    def list_contributors_of_project(self, pid):
        listings = self.__contributors.get(project_id = pid)
        listings = [ str(user) for user in listings ]
        return ("ok", json.dumps(listings))

    def compare_versions(self, client_version):
        if client_version != self.version:
            status = "fail"
            reason = "Mismatched versions. " +\
                    "This server uses version {}".format(self.version)
            response = (status, reason)
        else:
            status = "ok"
            reason = ""

        return (status, reason)

    # Utility

    # Just header-like stuff
    def get_project_metadata(self, owner, pid):
        """
        TODO: Do fs stuff properly
        """
        filename = pid + ".meta"
        relpath = os.path.join(owner, filename)
        fullpath = os.path.join(self.__project_root, relpath)
        with open(fullpath, "r") as f:
            content = f.read()
        return content

    # Get full project contents, including header-like stuff and notes, etc
    def get_project_contents(self, owner, pid):
        """
        TODO: Do fs stuff properly
        """
        meta = self.get_project_metadata(owner, pid)

        filename = pid + ".composte"
        relpath = os.path.join(owner, filename)
        fullpath = os.path.join(self.__project_root, relpath)
        with open(fullpath, "r") as f:
            content = f.read()
        return (meta, content)

    # Cookie: uuid
    def generate_cookie_for(self, user, project):
        """
        We don't bother checking for UUID collisions, since they "don't"
        happen
        """
        cookie = uuid.uuid4()
        self.sessions[cookie] = (user, project)
        return cookie

    # Session: {user, project}
    def cookie_to_session(self, cookie):
        return self.sessions[cookie]

    def remove_cookie(self, cookie):
        try:
            cookie = uuid.UUID(cookie)
        except ValueError as e:
            return ("fail", "That doesn't look like a cookie")

        try:
            del self.sessions[cookie]
        except KeyError as e:
            return ("fail", "Who are you")

        return ("ok", "")

    def do_update(self, args):
        try:
            musicWrapper.performMusicFun(*args)
        except e:
            return ("fail", "Internal Server Error")
        return ("ok", "")

    # TODO: Actually get the damn project (and bump refcount)
    def subscribe(self, username, pid):
        # Assert permission
        contributors = self.__contributors.get(project_id = pid)
        contributors = [ user.uname for user in contributors ]
        if username in contributors:
            cookie = self.generate_cookie_for(username, pid)
            return ("ok", cookie)
        else:
            return ("fail", "You are not a contributor")

    # Un-get the damn project(and un-bump refcount)
    def unsubscribe(self, cookie):
        return self.remove_cookie(cookie)

    # Packaged for neatness
    def get_db_connections(self):
        dbname = "data/composte.db"

        if self.__users is None:
            self.__users = driver.Auth(dbname)

        if self.__projects is None:
            self.__projects = driver.Projects(dbname)

        if self.__contributors is None:
            self.__contributors = driver.Contributors(dbname)

    # Handlers

    def __handle(self, _, rpc):
        self.get_db_connections()

        self.__server.debug(rpc)
        f = rpc["fName"]
        if f == "register":
            reply = self.register(*rpc["args"])
        elif f == "login":
            reply = self.login(*rpc["args"])
        elif f == "create_project":
            reply = self.create_project(*rpc["args"])
        elif f == "list_projects":
            reply = self.list_projects_by_user(*rpc["args"])
        elif f == "get_project":
            reply = self.get_project(*rpc["args"])
        elif f == "subscribe":
            reply = self.subscribe(*rpc["args"])
        elif f == "unsubscribe":
            reply = self.unsubscribe(*rpc["args"])
        elif f == "update":
            # Presumably, we want to broadcast, but this brings up an annoying
            # issue for clients: They need to filter out which broadcasts are
            # meant for them and which ones aren't
            self.__server.broadcast(server.serialize(rpc))
            reply = ("?", "?")
            # This function signature needs some work if it's the single
            # exposed function.
            # reply = musicWrapper.performMusicFun(rpc["project_ID"], None,
            # *rpc["args"], ???????, ????????) # Fuck
        elif f == "handshake":
            reply = self.compare_versions(*rpc["args"])
        else:
            reply = ("fail", "Unrecognized command")

        return server.serialize(*reply)

    # Probably deserialization
    def __preprocess(self, message):
        return client.deserialize(message)

    def __postprocess(self, message):
        return message

    def stop(self):
        self.__server.stop()

def stop_server(sig, frame, server):
    server.stop()
    print()

if __name__ == "__main__":
    import signal

    version = get_version()
    print("Composte server version {}".format(version))

    s = ComposteServer("tcp://*:6666", "tcp://*:6667", StdErr, Encryption())

    signal.signal(signal.SIGINT , lambda sig, f: stop_server(sig, f, s))
    signal.signal(signal.SIGQUIT, lambda sig, f: stop_server(sig, f, s))
    signal.signal(signal.SIGTERM, lambda sig, f: stop_server(sig, f, s))

