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
from network.base.loggable import DevNull, StdErr, Combined
from network.base.exceptions import GenericError

from network.conf import logging as networkLog
import logging

from protocol import client, server

from auth import auth
from database import driver

from util import musicWrapper, bookkeeping, composteProject, timer, misc

from threading import Thread, Lock
import uuid
import json
import os
import sqlite3

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

        self.version = misc.get_version()
        self.__server.info("Composte server version {}".format(self.version))

        self.__data_root = data_root
        self.__project_root = os.path.join(self.__data_root, "users")

        # This is a dummy function
        self.__dlock = Lock()
        self.__done = False

        self.__pool = bookkeeping.ProjectPool()
        # A better solution would have a lock for every project, but in a
        # classroom demo this won't be an issue
        self.__flushing = Lock()

        def is_done(self):
            with self.__dlock:
                return not self.__done

        self.__timer = timer.every(300, 2,
                lambda: self.__pool.map(self.flush_project),
                lambda: is_done(self))

        try:
            os.makedirs(self.__project_root)
        except FileExistsError as e:
            pass

        self.sessions = {}

    def flush_project(self, project, count):
        with self.__flushing:
            self.write_project(project)

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

    def create_project(self, uname, pname, metadata):
        metadata = json.loads(metadata)

        proj = composteProject.ComposteProject(metadata)
        id_ = str(proj.projectID)

        self.write_project(proj)

        try:
            self.__projects.put(id_, pname, uname)
        except sqlite3.OperationalError as e:
            self.__server.info("?????????????")
            raise GenericError("The database is fucked")

        hopefully_not_None = self.__users.get(uname)
        if hopefully_not_None is None:
            return ("fail", "User {} is not registered".format(uname))

        # This could then potentially also lock the database...
        try:
            self.__contributors.put(uname, id_)
        except sqlite3.IntegrityError as e:
            raise e
            return ("fail", "User {} is not registered".format(uname))

        return ("ok", id_)

    def get_project_over_the_wire(self, pid):
        (status, proj) = self.get_project(pid)

        return (status, proj.serialize())

    def get_project(self, pid):
        project_entry = self.__projects.get(pid)
        if project_entry.id == None:
            return ("fail", "Project not found")

        pid = project_entry.id
        owner = project_entry.owner

        proj = self.read_project(pid)

        return ("ok", proj)

    # TODO: This can probably fail
    def list_projects_by_user(self, uname):
        listings = self.__contributors.get(username = uname)
        listings = [ str(project) for project in listings ]
        return ("ok", json.dumps(listings))

    # TODO: This can probably fail
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

    def write_project(self, project):
        """
        I'm going to cheat for now and dump to the filesystem. Ideally we
        write to a database, but that requires more work. Either way, that can
        be hidden in this function
        """
        user = project.metadata["owner"]
        id_ = str(project.projectID)

        (parts, metadata, _) = project.serialize()

        base_path = os.path.join(self.__project_root, user)
        base_path = os.path.join(base_path, id_)
        with open(base_path + ".meta", "w") as f:
            f.write(metadata)

        with open(base_path + ".composte", "w") as f:
            f.write(parts)

    def read_project(self, pid):
        """
        We've cheated and the projects live on the filesystem. Ideally we want
        them in a database, but that's work. Either way, we hide the true
        locations of projects inside of this function.
        """

        owner = self.__projects.get(pid).owner

        filename = pid + ".meta"
        relpath = os.path.join(owner, filename)
        fullpath = os.path.join(self.__project_root, relpath)
        with open(fullpath, "r") as f:
            metadata = f.read()

        filename = pid + ".composte"
        relpath = os.path.join(owner, filename)
        fullpath = os.path.join(self.__project_root, relpath)
        with open(fullpath, "r") as f:
            parts = f.read()

        project = composteProject.deserializeProject(
            (parts, metadata, pid)
        )
        # Don't put it into the pool yet, because then we end up with a
        # use count that will never be 0 again
        return project

    # Cookie: uuid
    def generate_cookie_for(self, user, project):
        """
        We don't bother checking for UUID collisions, since they "don't"
        happen
        """
        cookie = uuid.uuid4()
        self.sessions[cookie] = (user, project)
        return cookie

    # Session: {user, project_id}
    # May need login cookies too...
    def cookie_to_session(self, cookie):
        try:
            cookie = uuid.UUID(cookie)
        except ValueError as e:
            return ("fail", "That doesn't look like a cookie")

        try:
            session = self.sessions[cookie]
        except KeyError as e:
            return None
        return session

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

        # Use this function to get a project
        def get_fun(pid):
            # The client musicfuns shouldn't have to worry about how the
            # server manages the lifetimes of project objects
            proj = self.__pool.put(pid, lambda: self.get_project(pid)[1])
            self.__pool.remove(pid)
            return proj

        with self.__flushing:
            try:
                # We still need to provide a way to get the project
                reply = musicWrapper.performMusicFun(*args, fetchProject = get_fun)
            except e:
                return ("fail", "Internal Server Error")
            return reply

    def subscribe(self, username, pid):
        # Assert permission
        contributors = self.__contributors.get(project_id = pid)
        contributors = [ user.uname for user in contributors ]
        if username in contributors:
            self.__pool.put(pid, lambda: self.get_project(pid)[1])
            cookie = self.generate_cookie_for(username, pid)
            return ("ok", cookie)
        else:
            return ("fail", "You are not a contributor")

    def unsubscribe(self, cookie):
        session = self.cookie_to_session(cookie)

        if session is None:
            return ("fail", "You are not subscribed")

        (user, project_id) = session
        (status, reason) = self.remove_cookie(cookie)

        if status == "ok":
            project = self.__pool.put(project_id,
                    lambda x: self.get_project(x)[1])
            pid = project.projectID
            self.__pool.remove(pid, lambda x: self.write_project(x))

        return (status, reason)

    # Packaged for neatness
    def get_db_connections(self):
        dbname = "data/composte.db"

        if self.__users is None:
            self.__users = driver.Auth(dbname)

        if self.__projects is None:
            self.__projects = driver.Projects(dbname)

        if self.__contributors is None:
            self.__contributors = driver.Contributors(dbname)

    def share(self, pid, new_contributor):
        """
        Add a new user to the list of contributors to a project
        """

        contributors = self.__contributors.get(project_id = pid)
        user = self.__users.get(new_contributor)

        # If that's not a known user, fail
        if user.uname is None:
            return ("fail", "Who is that")

        # If they are already a contributor, nothing to do
        if new_contributor not in contributors:
            # If that's not a valid project, fail
            try:
                self.__contributors.put(new_contributor, pid)
            except sqlite3.IntegrityError as e:
                return ("fail", "What project is that")

        return ("ok", "")

    # Handlers

    def __handle(self, _, rpc):
        self.get_db_connections()

        def fail(*args):
            return ("fail", "I don't know what you want me to do")

        def unimplemented(*args):
            return ("?", "?")

        rpc_funs = {
            "register": self.register,
            "login": self.login,
            "create_project": self.create_project,
            "list_projects": self.list_projects_by_user,
            "get_project": self.get_project_over_the_wire,
            "subscribe": self.subscribe,
            "unsubscribe": self.unsubscribe,
            "update": self.do_update,
            "handshake": self.compare_versions,
            "share": self.share,
        }

        self.__server.debug(rpc)
        f = rpc["fName"]

        do_rpc = rpc_funs.get(f, fail)

        try:
            # This is expected to be a tuple of things to send back
            (status, other) = do_rpc(*rpc["args"])
        except GenericError as e:
            return ("fail", "Internal server error")
        except:
            return ("fail", "Internal server error (Developer error)")

        # Only broadcast successful updates
        if f == "update" and status == "ok":
            self.__server.broadcast(server.serialize(rpc))

        return (status, other)

    # Probably deserialization
    def __preprocess(self, message):
        return client.deserialize(message)

    def __postprocess(self, reply):
        reply_str = server.serialize(*reply)
        self.__server.debug(reply_str)
        return reply_str

    def stop(self):
        with self.__dlock:
            self.__done = True

        self.__timer.join()
        self.__pool.map(self.flush_project)

        self.__server.stop()

def stop_server(sig, frame, server):
    server.stop()

if __name__ == "__main__":
    import signal

    import argparse

    parser = argparse.ArgumentParser(prog = "ComposteServer",
            description = "A Composte Server")

    parser.add_argument("-i", "--interactive-port", default = 5000,
            type = int)
    parser.add_argument("-b", "--broadcast-port", default = 5001,
            type = int)

    args = parser.parse_args()

    print("Composte server version {}".format(misc.get_version()))

    networkLog.setup()
    log = logging.getLogger("main")

    real_log = Combined((log, StdErr))

    s = ComposteServer("tcp://*:{}".format(args.interactive_port),
            "tcp://*:{}".format(args.broadcast_port), real_log, Encryption())

    signal.signal(signal.SIGINT , lambda sig, f: stop_server(sig, f, s))
    signal.signal(signal.SIGQUIT, lambda sig, f: stop_server(sig, f, s))
    signal.signal(signal.SIGTERM, lambda sig, f: stop_server(sig, f, s))

