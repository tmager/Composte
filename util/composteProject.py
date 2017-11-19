import music21
import uuid

class ComposteProject: 
    def __init__(self, owner, metadata):
        """ Initializes the Project with an empty stream, 
            a list of subscribers consisting solely of the owner, 
            and a dictionary of metadata about the score. """
        self.parts = [music21.stream.Stream()]
        self.subscribers = [owner]
        self.metadata = metadata
        self.projectID = uuid.uuid4()
    
    def addPart(self): 
        """ Adds a new part to a project. """
        self.parts.append(music21.stream.Stream())

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

    def pickleIndividualPart(self, partIndex): 
        """ Pickle a single part of music21 data in a project. """
        return music21.converter.freezeStr(self.parts[partIndex])

    def pickleAllParts(self): 
        """ Pickle all parts of music21 data in a project. """
        return music21.converter.freezeStr(self.parts) 

    def pickleObjectsAtPartOffset(self, offset, partIndex): 
        """ Pickle all objects at a given part offset to a client. """
        objs = parts[partIndex].getElementsByOffset(offset) 
        return music21.converter.freezeStr(objs)


