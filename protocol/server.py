#!/usr/bin/env python3

import json
import music21

from base.exceptions import DeserializationFailure

def serialize(status, *args):
    return json.dumps(
        [status, [str(arg) for arg in args]]
    )

def deserialize(msg):
    pythonObject = json.loads(msg)
    if type(pythonObject) != dict:
        raise DeserializationFailure("Received malformed data: {}".format(msg))
    return pythonObject

# =================================================================================

import os, sys
import subprocess

def version():
    here = os.path.basename(__file__)

    p = subprocess.Popen(["git", "log", "-1"], stdout = subprocess.PIPE)

    with p.stdout:
        hash_ = p.stdout.readline().decode().split(" ")[-1]

    return hash_.strip()

if __name__ == "__main__":
    print(version())

