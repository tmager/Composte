#!/usr/bin/env python3

import json
import music21

from base.exceptions import DeserializationFailure

def serialize(username, projectID, function_name, *args):
    """ username =:= type(str) 
        projectID =:= type(ComposteProject.projectID) 
        function_name =:= type(str) 
        args =:= type(list of str)
        """ 
    rpc = {
        "username": username
        "projectID": projectID
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

