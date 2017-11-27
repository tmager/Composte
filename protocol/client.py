#!/usr/bin/env python3

import json
import music21

from protocol.base.exceptions import DeserializationFailure

def serialize(function_name, *args):
    """
    function_name =:= type(str)
    args =:= type(list of str)
    """

    rpc = {
        "fName": function_name,
        "args": [str(arg) for arg in args],
    }

    return json.dumps(rpc)

def deserialize(msg):
    pythonObject = json.loads(msg)
    if type(pythonObject) != dict:
        raise DeserializationFailure("Received malformed data: {}".format(msg))
    return pythonObject

# =================================================================================

