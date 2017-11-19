#!/usr/bin/env python3

import json
import music21

from base.exceptions import DeserializationFailure

def serialize(function_name, *args):
    rpc = {
        "fName": function_name,
        "args": [str(arg) for arg in args],
    }

    return json.dunps(rpc)

def deserialize(msg):
    pythonObject = json.loads(msg)
    if type(pythonObject) != dict:
        raise DeserializationFailure("Received malformed data: {}".format(msg))
    return pythonObject

# =================================================================================

