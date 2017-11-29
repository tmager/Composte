# Wrapper for musicFuns.py
# All json data is assumed to be deserialized by
# the time these utility functions are invoked.
# Furthermore, the project on which to perform
# the desired function must have been determined
# before these functions are called.

from util import musicFuns
from util import composteProject
import music21

def performMusicFun(projectID, fname, args, partIndex=None, offset=None):
    """ Wrapper for all music functions, where the
        name of the function to be called (as a string)
        is the first argument, and the arguments to the
        function (as a list) is the second. """
    def unpickleMusicData(inputStr):
        """ Unpickles music21 data into a music21 stream """
        return music21.converter.thawStr(inputStr)
    def unpackFun(fname, args):
        """ Determines which function to call and
            casts all arguments to the correct types. """
        if fname == 'changeKeySignature':
            return (musicFuns.changeKeySignature, [float(args[0]),
                    unpickleMusicData(args[1]), int(args[2])])
        elif fname == 'insertNote':
            return (musicFuns.insertNote, [float(args[0]),
                    unpickleMusicData(args[1]), args[2],
                    float(args[3])])
        elif fname == 'removeNote':
            return (musicFuns.removeNote, [float(args[0]),
                    unpickleMusicData(args[1]), args[2]])
        elif fname == 'insertMetronomeMark':
            return (musicFuns.insertMetronomeMark, [float(args[0]),
                    unpickleMusicData(args[1]), args[2],
                    int(args[3]), float(args[4])])
        elif fname == 'removeMetronomeMark':
            return (musicFuns.removeMetronomeMark, [float(args[0]),
                    unpickleMusicData(args[1])])
        elif fname == 'transpose':
            return (musicFuns.transpose, [unpickleMusicData(args[0]),
                    int(args[1])])
        elif fname == 'insertClef':
            return (musicFuns.insertClef, [float(args[0]),
                    unpickleMusicData(args[1]), args[2]])
        elif fname == 'removeClef':
            return (musicFuns.removeClef, [float(args[0]),
                    unpickleMusicData(args[1])])
        elif fname == 'insertMeasures':
            return (musicFuns.insertMeasures, [float(args[0]),
                    unpickleMusicData(args[1]), float(args[2])])
        elif fname == 'addInstrument':
            return (musicFuns.addInstrument, [float(args[0]),
                    unpickleMusicData(args[1]), args[2]])
        elif fname == 'removeInstrument':
            return (musicFuns.removeInstrument, [float(args[0]),
                    unpickleMusicData(args[1])])
        elif fname == 'addDynamic':
            return (musicFuns.addDynamic, [float(args[0]),
                    unpickleMusicData(args[1]), args[2]])
        elif fname == 'removeDynamic':
            return (musicFuns.removeDynamic, [float(args[0]),
                    unpickleMusicData(args[1])])
        elif fname == 'addLyric':
            return (musicFuns.addLyric, [float(args[0]),
                    unpickleMusicData(args[1]), args[2]])
        else:
            return (("fail", "INVALID OPERATION"), None)

    (function, arguments) = unpackFun(fname, args)
    (status, alterations) = function(arguments)
    # TODO: Uncomment next line when database lookup is actually implemented
    # project = findProject(projectID)
    if partIndex is not None and offset is not None:
        project.updatePartAtOffset(alterations, partIndex, offset)
    elif partIndex is not None:
        project.updatePart(alterations, partIndex)
    else:
        project.updateParts(alterations)
    # TODO: Caching layer? Don't want to consult the database on every update, 
    # that may be way too slow.
    return status

