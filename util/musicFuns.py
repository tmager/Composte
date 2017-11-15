import music21

# The server always needs to know WHERE to make 
# an update, and needs to send that information 
# to all connected clients. Thus, the offset from
# the beginning of the piece (in quarterLengths, or "qLs")
# must always be given as the first argument to all
# update functions. Also, the server must know WHICH 
# part to apply the update in, hence the need to
# pass it as the second argument in all cases.

# Since rests are simply portions of the music where
# no sound is made, they do not need to be explicitly 
# notated in the backend representation. Also, 
# since ties across barlines only depend on a note's 
# duration, the GUI can figure out where to put 
# rests and where to put ties without having to 
# explicitly define them on the backend.

# Though music21 allows explicit definitions of which 
# 8th/16th notes (and below) should be beamed together
# into a single unit, this is wildly unnecessary for 
# our application. Correct beaming would be the job of
# the GUI, and our GUI may not even address beaming whatsoever.
# Likewise, for this initial implemenation, articulations
# expressions, and different clefs besides treble remain 
# unimplemented. 

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
            representing the index of the parts to swap. """
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

def changeKeySig(offset, part, newSigSharps): 
    """ Changes the Key Signature at a given offset inside a part. 
        Must provide the correct number of sharps in the key signature
        as an integer. Negative numbers correspond to the number of flats. """
    newKeySig = music21.key.KeySignature(newSigSharps)
    oldKeySigs = part.getKeySignatures()
    for i in range(len(oldKeySigs)): 
        if oldKeySigs[i].offset == offset: 
            part.replace(oldKeySigs[i], newKeySig)
            if i + 1 == len(oldKeySigs): 
                renameNotes(offset, part, newKeySig)
            else: 
                renameNotes(offset, part, newKeySig, oldKeySigs[i + 1].offset)
            # Broadcast the whole file 
            return
    part.insert(offset, newKeySig)
    for oldKeySig in oldKeySigs: 
        if offset < oldKeySig.offset: 
            renameNotes(offset, part, newKeySig, oldKeySig.offset) 
            # Broadcast the whole file 
            return
    renameNotes(offset, part, newKeySig)
    # Broadcast the whole file
  
def renameNotes(startOffset, part, keySig, endOffset=None):
    """ Rename all notes affected by a key signature change
        intelligently so as to not have sharp accidentals
        in a flat key signature. Diffs need to accumulate 
        while the renaming is in process. """
    notes = part.notes
    hasSharps = 0 < keySig.sharps 
    for note in notes: 
        offset = note.offset
        if endOffset is None: 
            if startOffset <= offset: 
                part.replace(note, renameNote(note, hasSharps))
        else: 
            if startOffset <= offset and offset <= endOffset:
                part.replace(note, renameNote(note, hasSharps))

def renameNote(note, hasSharps):       
    """ Rename a note intelligently within a key. """
    name = note.name
    if hasSharps:
        if name[1] == '-': 
            noteName = name[0]
            if noteName == 'A': 
                newName = 'G'
            else: 
                newName = chr(ord(noteName) - 1)
            newName += '#'
            note.name = newName
    else: 
        if name[1] == '#': 
            noteName = name[0]
            if noteName == 'G': 
                newName = 'A'
            else: 
                newName = chr(ord(noteName) + 1) 
            newName += '-'
            note.name = newName
    return note
                
def changeTimeSignature(offset, part, newSigStr): 
    """ Changes the Time Signature at a given offset inside a part. 
        newTimeSig must be a string representing the new time signature, 
        such as '4/4' or '6/8'. """
    newTimeSig = music21.meter.TimeSignature(newSigStr)
    oldTimeSigs = part.getTimeSignatures()
    for oldTimeSig in oldTimeSigs: 
        if oldTimeSig.offset == offset: 
            part.replace(oldTimeSig, newTimeSig)
            # Broadcast
    part.insert(offset, newTimeSig)
    # Broadcast

def insertMetronomeMark(offset, parts, mark): 
    """ Insert a metronome marking in a list of
        parts at a given offset. """
    for part in parts: 
        markings = part.metronomeMarkBoundaries()
        for marking in markings: 
            # Marking already exists at that location, so update it
            if marking[0] == offset: 
                marking[2] = mark
                # Broadcast 
        part.insert(offset, mark)
        # Broadcast

def removeMetronomeMark(offset, parts, mark): 
    """ Remove a metronome marking from each part in
        a list of parts at a given offset. """
    for part in parts: 
        markings = part.metronomeMarkBoundaries()
        for marking in markings: 
            if marking[0] == offset: 
                part.remove(mark)
    # Broadcasts

def makeMetronomeMark(text, bpm, pulseQLduration, marksMade): 
    """ Make a metronome marking that can be uniquely identified as 
        an object during removal if removal is necessary."""
    mark = music21.tempo.MetronomeMark(text, bpm, pulseQLduration)
    mark.id = marksMade[0]
    marksMade[0] += 1
    return mark

def insertNote(offset, part, newNote): 
    """ Add a note at a given offset to a part. """
    part.insert(offset, newNote) 
    # Broadcast

def appendNote(part, newNote): 
    """ Add a note at the end of a part. """
    part.append(newNote)
    # Broadcast

def removeNote(offset, part, removedNoteName): 
    """ Remove a note at a given offset into a part. """
    notes = part.notes
    for note in notes: 
        noteName = note.pitch.nameWithOctave
        if note.offset == offset and noteName == removedNoteName: 
            part.remove(note)
    # Broadcast

def createNote(pitchName, durationInQLs): 
    """ Creates a Note from the name of a pitch 
        and a duration in quarter lengths. """
    note = music21.note.Note(pitchName)
    note.duration = music21.duration.Duration(durationInQLs)
    return note

def updateTieStatus(offset, part, noteName): 
    """ Updates the tie status of a note with the name noteName
        at a given offset into a given part. The offset given to
        this function MUST be the same as the offset of the 
        FIRST note in a legally tie-able pair of notes (the notes
        must be the same pitch, and there must be no rests between them)."""
    notes = part.notes
    for note in notes: 
        pitchStr = note.pitch.nameWithOctave
        if note.offset == offset and pitchStr == noteName: 
            qL = note.duration.quarterLength
            tieCantidates = part.getElementsByOffset(note.offset + qL)
            for cantidate in tieCantidates: 
                if cantidate.pitch.nameWithOctave == noteName: 
                    makeTieUpdate([note, cantidate])
                else: 
                    pass
            return # Saves some processor cycles by exiting the loop early
    
def makeTieUpdate(notes): 
    """ If the pair of notes passed to this function is untied, 
        this function ties them together. If ther pair of notes
        passed to this function is tied, the tie is severed. """
    [firstNote, secondNote] = notes
    # Add Ties
    if firstNote.tie is None and secondNote.tie is None: 
        firstNote.tie = music21.tie.Tie("start")
        secondNote.tie = music21.tie.Tie("stop")
    elif firstNote.tie.type == "stop" and secondNote.tie is None: 
        firstNote.tie.type = "continue" 
        secondNote.tie = music21.tie.Tie("stop")
    elif firstNote.tie is None and secondNote.tie.type == "start": 
        firstNote.tie = music21.tie.Tie("start")
        secondNote.tie.type = "continue"
    elif firstNote.tie.type == "stop" and secondNote.tie.type == "start": 
        firstNote.tie.type = "continue"
        secondNote.tie.type = "continue"
    # Remove Ties
    elif firstNote.tie.type == "start" and secondNote.tie.type == "stop": 
        firstNote.tie = None
        secondNote.tie = None
    elif firstNote.tie.type == "start" and secondNote.tie.type == "continue": 
        firstNote.tie = None
        secondNote.tie.type = "start"
    elif firstNote.tie.type == "continue" and secondNote.tie.type == "continue": 
        firstNote.tie.type = "stop"
        secondNote.tie.type = "start"
    elif firstNote.tie.type == "continue" and secondNote.tie.type == "stop": 
        firstNote.tie.type = "stop" 
        secondNote.tie = None
    # For completeness and defense against race conditions
    else: 
        pass 

def transpose(part, semitones): 
    """ Transposes the whole part up or down 
        by an integer number of semitones. """
    part.transpose(semitones, inPlace=True)
    # Broadcast whole file

def insertMeasures(insertionOffset, part, insertedQLs): 
    """ Insert measures in a part by moving the offsets of 
        portions of the score by a given number of QLs. """
    part.shiftElements(insertedQLs, insertionOffset)
    # Broadcast whole file

def sendAllParts(project): 
    """ Send all parts of music21 data 
        in a project to a client. """
    parts = project.parts
    for part in parts: 
        sendPart(part)

def sendPart(part): 
    """ Send a single part of music21 data 
        in a project to a client. """
    stream = part.offsetMap()
    # Broadcast stream to client

def sendObjectsAtPartOffset(offset, part): 
    """ Send all objects at a given part offset to a client. """
    # Broadcast objs to client
    objs = filter(lambda x: x.offset == offset, part) 

def addLyric(offset, part, lyric): 
    """ Add lyrics to a given note in the score. """
    notes = part.notes
    for note in notes: 
        if note.offset == offset: 
            note.addLyric(lyric)
            # Broadcast success
            return
    # Broadcast failure
