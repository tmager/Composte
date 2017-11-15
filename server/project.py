import music21

class Project: 
    def __init__(self, owner, metadata):
        """ Initializes the Project with an empty stream, 
            a list of subscribers consisting solely of the owner, 
            and a dictionary of metadata about the score. """
        self.parts = [music21.stream.Stream()]
        self.subscribers = [owner]
        self.metadata = metadata
    
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

    def addSubscriber(self, user): 
        """ Adds a new subscriber to the project. """
        self.subscribers.append(user)

    def removeSubscriber(self, user): 
        """ Removes a subscriber from a project. """
        self.subscribers.remove(user)

    def sendAllParts(self): 
        """ Send all parts of music21 data 
            in a project to a client. """
        def sendPart(part): 
            """ Send a single part of music21 data 
                in a project to a client. """
            stream = music21.converter.freezeStr(part)
            # Broadcast stream to client
        parts = project.parts
        for part in parts: 
            sendPart(part)
    
    def sendObjectsAtPartOffset(offset, part): 
        """ Send all objects at a given part offset to a client. """
        # Broadcast objs to client
        objs = part.getElementsByOffset(offset) 
        frozen = music21.converter.freezeStr(objs)
        thawed = music21.converter.thawStr(frozen)
        print(thawed) 
