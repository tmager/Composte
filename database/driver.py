#!/usr/bin/env python3

import sqlite3
from threading import Lock

# We are inspired by Django, but we're not that good at
# introspection/reflection

# There's a potential concurrency issue here, but we'll ignore it for now:
# Multiple writes in flight at once can corrupt the databsae. I'm not sure if
# using a single sqlite connection is enough to serialize writes/updates
class SingletonsAreWeird:
    __instances = {}

    # Ugh
    def __new__(class_, db, init):
        if db not in SingletonsAreWeird.__instances:
            SingletonsAreWeird.__instances[db] = sqlite3.connect(db)
            init(SingletonsAreWeird.__instances[db])
        return SingletonsAreWeird.__instances[db]

def enforce_foreign_key(conn):
    conn.execute("PRAGMA foreign_keys = \"1\"")
    conn.commit()

class Auth:
    # We're so bad at CRUD that we only bother to do half of it
    __blueprint = ("username", "hash", "email")

    def __init__(self):
        self.__conn = SingletonsAreWeird("composte.db", enforce_foreign_key)
        print(id(self.__conn))
        self.__cursor = self.__conn.cursor()

        self.__cursor.execute(""" CREATE TABLE IF NOT EXISTS auth
                ( username TEXT PRIMARY KEY NOT NULL,
                  hash TEXT NOT NULL,
                  email TEXT)""")
        self.__conn.commit()
        self.__lock = Lock()

    # Create
    def put(self, username, hash_, email = "null"):
        self.__cursor.execute("""
                INSERT INTO auth (username, hash, email)
                VALUES (?, ?, ?)
                """, (username, hash_, email))
        self.__conn.commit()

    # Retrieve
    def get(self, username):
        with self.__lock:
            self.__cursor.execute("""
                    SELECT * FROM auth WHERE username=?
                    """, (username,))
            return self.__cursor.fetchone()

# Project storage path is always
#   //owner/id.{meta,proj}
class Projects:
    __blueprint = ("id", "name", "owner")

    def __init__(self):
        self.__conn = SingletonsAreWeird("composte.db", enforce_foreign_key)
        print(id(self.__conn))
        self.__cursor = self.__conn.cursor()

        self.__cursor.execute("""
                CREATE TABLE IF NOT EXISTS projects
                ( id TEXT PRIMARY KEY NOT NULL,
                  name TEXT NOT NULL,
                  owner TEXT NOT NULL REFERENCES auth(username))""")

        self.__conn.commit()

        self.__lock = Lock()

    def put(self, id_, name, owner):
        self.__cursor.execute("""
                INSERT INTO projects (id, name, owner)
                VALUES (?, ?, ?)
                """, (id_, name, owner))
        self.__conn.commit()

    def get(self, id_):
        with self.__lock:
            self.__cursor.execute("""
                    SELECT * FROM projects WHERE id=?
                    """, (id_,))
            return self.__conn.fetchone()

class Contributors:
    def __init__(self):
        self.__conn = SingletonsAreWeird("composte.db", enforce_foreign_key)
        print(id(self.__conn))
        self.__cursor = self.__conn.cursor()

        self.__cursor.execute("""
                CREATE TABLE IF NOT EXISTS contributors (
                    username TEXT NOT NULL REFERENCES auth(username),
                    project_id TEXT NOT NULL REFERENCES projects(id),
                    PRIMARY KEY (username, project_id)) """)
        self.__conn.commit()

        self.__lock = Lock()

    def put(self, username, project_id):
        self.__cursor.execute("""
                INSERT INTO contributors (username, project_id)
                VALUES (?, ?)
                """, (username, project_id))
        self.__conn.commit()

    def get(self, username = None, project_id = None):
        # What are you even doing at this point?
        if username is None and project_id is None:
            return None
        # Want all users attached to a project
        if username is None:
            return self.get_users(project_id)
        # Want all projects attached to user
        if project_id is None:
            return self.get_projects(username)

        # ??????
        return None

    def get_users(self, project_id):
        with self.__lock:
            self.__cursor.execute("""
                    SELECT username FROM contributors
                    WHERE project_id=?
                    """, (project_id,))
            return self.__cursor.fetchone()

    def get_projects(self, username):
        with self.__lock:
            self.__cursor.execute("""
                    SELECT project_id from contributors
                    WHERE username=?
                    """, (username,))
            return self.__cursor.fetchone()

if __name__ == "__main__":
    import os

    try:
        os.remove("composte.db")
    except:
        pass

    auth  = Auth()
    proj = Projects()
    own = Contributors()

    auth.put("shark meldon", "there", "hello@composte.me")
    auth.put("save me", "whee", "saveme@composte.me")

    proj.put("1", "a", "save me")
    proj.put("2", "b", "shark meldon")

    own.put("shark meldon", "1")
    own.put("shark meldon", "2")

    # own.put("not", "real")

