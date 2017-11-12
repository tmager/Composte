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
    def __init__(self):
        self.parts = [music21.stream.Stream()]
        self.metadata = {}
    
def changeKeySig(offset, part, newKeySig): 
    """ Changes the Key Signature at a given offset inside a part """
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
                
def changeTimeSig(offset, part, newTimeSig): 
    """ Changes the Time Signature at a given offset inside a part """
    oldTimeSigs = part.getTimeSignatures()
    for oldTimeSig in timeSigs: 
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
                # Broadcast success
                return
        # Broadcast failure

def makeMetronomeMark(text, bpm, pulseQLduration, marksMade): 
    """ Make a metronome marking that can be uniquely identified as 
        an object during removal if removal is necessary."""
    mark = music21.tempo.MetronomeMark(text, bpm, pulseQLduration)
    mark.id = marksMade[0]
    marksMade[0] += 1
    return mark

def insertNote(offset, part, newNote): 
    """ Add a note at a given offset to a part. """
    notes = part.notes
    for note in notes: 
        if note.offset == offset: 
            note.add(newNote)
            # Broadcast
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
        if note.offset == offset: 
            try: 
                note.remove(removedNoteName) 
            except ValueError: 
                # The note was already removed, don't remove it again 
                pass
    # Broadcast

def createNote(pitchName, durationInQLs): 
    """ Creates a Note from the name of a pitch 
        and a duration in quarter lengths. """
    note = music21.note.Note(pitchName)
    note.duration = durationInQLs
    return note

def transpose(part, semitones): 
    """ Transposes the whole part up or down 
        by a number of semitones. """
    part.transpose(semitones)
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
