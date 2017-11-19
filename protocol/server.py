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

