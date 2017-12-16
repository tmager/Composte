# NOTE: This implementation still assumes that updates to 
# an individual project are serialized, but the server itself 
# can support concurrent updates of different projects. 

import music21
import uuid
import json
import base64
from network.base.exceptions import GenericError

class ComposteProject:
    def __init__(self, metadata, score=None, projectID=None):
        """ Initializes the Project with an empty score
            containing an empty part, where said empty part 
            contains an empty measure
            a list of subscribers consisting solely of the owner,
            and a dictionary of metadata about the score. """
        self.metadata = metadata

        if projectID is not None:
            self.projectID = projectID
        else:
            self.projectID = uuid.uuid4()

        if score is not None:
            self.score = score
        else:
            s = music21.stream.Score()
            p = music21.stream.Part()
            p.displayIndex = 0 # Included to help GUI show parts in order
            m = music21.stream.Measure()
            m.insert(0.0, music21.tempo.MetronomeMark("", 120, 1.0))
            p.insert(0.0, m)
            s.insert(0.0, p)
            self.score = s

    def addPart(self):
        """ Adds a new part to a project. """
        p = music21.stream.Part()
        p.displayIndex = len(self.score.parts)
        m = music21.stream.Measure()
        m.insert(0.0, music21.tempo.MetronomeMark("", 120, 1.0))
        p.insert(0.0, m)
        self.score.insert(0.0, p)

    def updateMetadata(self, fieldName, fieldValue):
        """ Allow updates to project metadata. """
        self.metadata[fieldName] = str(fieldValue)

    def swapParts(self, firstPartIndex, secondPartIndex):
        """ Swaps two parts in a project. This is purely cosmetic: all
            it will affect is the order in which parts are presented on
            the GUI. firstPartIndex and secondPartIndex are both 0-indexed 
            integers representing the indicies of the parts to swap. """
        if (int(firstPartIndex) < len(self.score.parts) and
            int(secondPartIndex) < len(self.score.parts)):
            fst = self.score.parts[firstPartIndex].displayIndex
            snd = self.score.parts[secondPartIndex].displayIndex
            self.score.parts[firstPartIndex].displayIndex = snd
            self.score.parts[secondPartIndex].displayIndex = fst
        else:
            raise GenericError

    def removePart(self, removeIndex):
        """ Remove a part from a project. removeIndex is a 0-indexed
            integer representing the index of the part to remove. """
        parts = self.score.parts
        if int(removeIndex) < len(parts):
            self.score.remove(parts[removeIndex])
            for i in range(0, len(parts)): 
                if removeIndex <= parts[i].displayIndex: 
                    parts[i].displayIndex = parts[i].displayIndex - 1
        else:
            raise GenericError

    def partIndexToDisplayIndex(self, displayIndex):
        """ Converts a backend part index 
            to a GUI-layer display index. """
        for i in range(0, len(self.score.parts)): 
            if self.score.parts[i].displayIndex == displayIndex: 
                return i
        return -1 # Sentinal value

    def displayIndexToPartIndex(self, partIndex):
        """ Converts a GUI-layer display index 
            to a backend part index. """
        try: 
            return self.score.parts[partIndex].displayIndex
        except IndexError: 
            return -1 # Sentinal value

    def serialize(self):
        """ Construct three JSON objects representing the fields of
            a ComposteProject. Intended to be stored in three
            discrete database fields. Returns a tuple containing the
            serialized JSON objects. """
        bits = music21.converter.freezeStr(self.score) 
        bytes_ = base64.b64encode(bits).decode()
        score = json.dumps(bytes_)
        metadata = json.dumps(self.metadata)
        id_ = str(self.projectID)
        return (metadata, score, id_)

def deserializeProject(serializedProject):
    """ Deserialize a serialized music21 composteProject
        into a composteProject object. """
    (metadata, score, id_) = serializedProject
    bits = json.loads(score)
    bytes_ = base64.b64decode(bits.encode())
    score = music21.converter.thawStr(bytes_)
    metadata = json.loads(metadata)
    id_ = uuid.UUID(id_)
    return ComposteProject(metadata, score, id_)

