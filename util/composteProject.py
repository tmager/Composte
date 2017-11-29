import music21
import uuid
import json

class ComposteProject:
    def __init__(self, metadata):
        """ Initializes the Project with an empty stream,
            a list of subscribers consisting solely of the owner,
            and a dictionary of metadata about the score. """
        self.parts = [music21.stream.Stream()]
        self.metadata = metadata
        self.projectID = uuid.uuid4()

    def __init__(self, parts, metadata, projectID): 
        """ Initializer for Projects which are loaded from
            disk, where all fields are already known, but 
            the ComposteProject object itself doesn't exist yet. """
        self.parts = parts
        self.metadata = metadata
        self.projectID = projectID

    def addPart(self):
        """ Adds a new part to a project. """
        self.parts.append(music21.stream.Stream())

    def updateMetadata(self, fieldName, fieldValue):
        """ Allow updates to project metadata. """
        self.metadata.fieldName = str(fieldValue)

    def swapParts(self, firstPart, secondPart):
        """ Swaps two parts in a project. This is purely cosmetic: all
            it will affect is the order in which parts are presented on
            the GUI. firstPart and secondPart are both 0-indexed integers
            representing the indicies of the parts to swap. """
        tmp = self.parts[firstPart]
        self.parts[firstPart] = self.parts[secondPart]
        self.parts[secondPart] = tmp

    def removePart(self, partToRemove):
        """ Remove a part from a project. partToRemove is a 0-indexed
            integer representing the index of the part to remove. """
        del self.parts[partToRemove]

    def updatePart(self, unpickledPart, partIndex):
        """ Updates an entire part as identified by a part index. """
        self.parts[partIndex] = unpickledPart

    def updatePartAtOffset(self, unpickledStream, partIndex, streamOffset):
        """ Updates a part at a given stream offset. """
        part = self.parts[partIndex]
        elems = part.getElementsByOffset(streamOffset)
        for elem in elems:
            part.remove(streamOffset, elem)
        for member in unpickledStream:
            part.insert(streamOffset, member)

    def updateParts(self, unpickledParts):
        """ Updates all parts with new part state. """
        for i in range(0, len(unpickledParts)):
            self.parts[i] = unpickledParts[i]

    def addSubscriber(self, user):
        """ Adds a new subscriber to the project. """
        self.subscribers.append(user)

    def removeSubscriber(self, user):
        """ Removes a subscriber from a project. """
        self.subscribers.remove(user)

    def pickleAllParts(self):
        """ Pickle all parts of music21 data in a project. """
        return music21.converter.freezeStr(self.parts)

    def serialize(self): 
        """ Construct three JSON objects representing the fields of
            a ComposteProject. Intended to be stored in three 
            discrete database fields. Returns a tuple containing the 
            serialized JSON objects. """
        parts = json.dumps(music21.converter.freezeStr(self.parts))
        metadata = json.dumps(self.metadata)
        uuid = json.dumps(self.projectID)
        return (parts, metadata, uuid)

def deserializeProject(serializedProject): 
    """ Deserialize a serialized music21 composteProject
        into a composteProject object. """
    (parts, metadata, uuid) = serializedProject
    parts = music21.converter.thawStr(json.loads(parts))
    metadata = json.loads(metadata)
    uuid = json.loads(uuid)
    return ComposteProject(parts, metadata, uuid)

