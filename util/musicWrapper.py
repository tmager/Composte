# Wrapper for musicFuns.py
# All json data is assumed to be deserialized by
# the time these utility functions are invoked.
# Furthermore, the project on which to perform
# the desired function must have been determined
# before these functions are called.

from util import musicFuns
from util import composteProject
from network.base.exceptions import GenericError
import music21
import json

def performMusicFun(projectID, fname, args, partIndex=None, offset=None,
        fetchProject=None):
    """ Wrapper for all music functions, where the
        name of the function to be called (as a string)
        is the first argument, and the arguments to the
        function (as a list) is the second. """
    # Fetch the project before anything else
    # for ease of use
    project = fetchProject(projectID)
    args = json.loads(args)

    def unpackFun(fname, args):
        """ Determines which function to call and
            casts all arguments to the correct types. """
        try:
            if partIndex is not None and partIndex != "None":
                musicObject = project.parts[int(partIndex)]
            else:
                musicObject = project.parts
            if fname == 'changeKeySignature':
                return (musicFuns.changeKeySignature, [float(args[0]),
                        musicObject, int(args[2])])
            elif fname == 'insertNote':
                return (musicFuns.insertNote, [float(args[0]),
                        musicObject, args[2], float(args[3])])
            elif fname == 'removeNote':
                return (musicFuns.removeNote, [float(args[0]),
                        musicObject, args[2]])
            elif fname == 'insertMetronomeMark':
                return (musicFuns.insertMetronomeMark, [float(args[0]),
                        musicObject, int(args[1])])
            elif fname == 'removeMetronomeMark':
                return (musicFuns.removeMetronomeMark, [float(args[0]),
                        musicObject])
            elif fname == 'transpose':
                return (musicFuns.transpose, [musicObject,
                        int(args[1])])
            elif fname == 'insertClef':
                return (musicFuns.insertClef, [float(args[0]),
                        musicObject, args[2]])
            elif fname == 'removeClef':
                return (musicFuns.removeClef, [float(args[0]),
                        musicObject])
            elif fname == 'insertMeasures':
                return (musicFuns.insertMeasures, [float(args[0]),
                        musicObject, float(args[2])])
            elif fname == 'addInstrument':
                return (musicFuns.addInstrument, [float(args[0]),
                        musicObject, args[2]])
            elif fname == 'removeInstrument':
                return (musicFuns.removeInstrument, [float(args[0]),
                        musicObject])
            elif fname == 'addDynamic':
                return (musicFuns.addDynamic, [float(args[0]),
                        musicObject, args[2]])
            elif fname == 'removeDynamic':
                return (musicFuns.removeDynamic, [float(args[0]),
                        musicObject])
            elif fname == 'addLyric':
                return (musicFuns.addLyric, [float(args[0]),
                        musicObject, args[2]])
            # Why not also make a chat server?
            elif fname == 'chat': 
                return (lambda : ("ok", ""), [])
            else:
                return (None, None)
        except ValueError as e:
            raise GenericError from e

    (function, arguments) = unpackFun(fname, args)
    # Begin error handling
    if (function, arguments) == (None, None):
        return ("fail", "INVALID OPERATION")

    if offset is not None and offset != 'None':
        if float(offset) < 0.0:
            raise GenericError

    try:
        updateOffsets = function(*arguments)
        if updateOffsets == ("ok", ""): 
            return ("ok", "")
    except music21.exceptions21.Music21Exception:
        raise GenericError

    # End error handling
    return ("ok", updateOffsets)

