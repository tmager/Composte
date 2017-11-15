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
# notated in the backend representation. 

# Though music21 allows explicit definitions of which 
# 8th/16th notes (and below) should be beamed together
# into a single unit, this is wildly unnecessary for 
# our application. Correct beaming would be the job of
# the GUI, and our GUI may not even address beaming whatsoever.
# Likewise, for this initial implemenation, articulations,
# expressions, and repeats remain unimplemented. 

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
    # Have to create a NEW Note object to use replace. Reasons unclear.
    name = note.name
    octave = note.octave
    duration = note.duration
    if hasSharps:
        if name[1] == '-': 
            noteName = name[0]
            if noteName == 'A':
                newName = 'G'
            else: 
                newName = chr(ord(noteName) - 1)
            newName += '#'
        else: 
            newName = name
    else: 
        if name[1] == '#': 
            noteName = name[0]
            if noteName == 'G': 
                newName = 'A'
            else: 
                newName = chr(ord(noteName) + 1) 
            newName += '-'
        else: 
            newName = name
    return createNote(newName + str(octave), duration.quarterLength)
                
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

def insertMetronomeMark(offset, parts, markData): 
    """ Insert a metronome marking in a list of
        parts at a given offset. markData is a tuple of 
        staff text as a string (for almost all purposes, this will 
        be the empty string), pulses per minute as an integer, and 
        the duration in quarterLengths of a single pulse as a
        float. When duration is 1.0, the second argument is 
        exactly equivalent to BPM (beats per minute). """
    mark = makeMetronomeMark(markData)
    for part in parts: 
        markings = part.metronomeMarkBoundaries()
        for marking in markings: 
            # Marking already exists at that location, so update it
            if marking[0] == offset: 
                marking[2] = mark
                # Broadcast 
        part.insert(offset, mark)
        # Broadcast

def removeMetronomeMark(offset, parts): 
    """ Remove a metronome marking from each part in
        a list of parts at a given offset. """
    for part in parts: 
        markings = part.metronomeMarkBoundaries()
        for marking in markings: 
            if marking[0] == offset: 
                part.remove(marking)
    # Broadcasts

def makeMetronomeMark(markData): 
    """ Make a metronome marking that can be uniquely identified as 
        an object during removal if removal is necessary."""
    (text, bpm, pulseQLduration) = markData
    mark = music21.tempo.MetronomeMark(text, bpm, pulseQLduration)
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
    note.pitch.spellingIsInferred = False
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

def insertClef(offset, part, clefStr): 
    """ Inserts a new clef at a given offset in a given part. 
        The types of clefs supported ON THE BACKEND are: 
        'treble', 'treble8va', 'treble8vb, 'bass', 'bass8va', 
        'bass8vb', 'frenchviolin', 'alto', 'tenor', 'cbaritone', 
        'fbaritone', 'gsoprano', 'mezzosoprano', 'soprano',
        'percussion', and 'tab'. """
    newClef = music21.clef.clefFromString(clefStr)
    elems = getElementsByOffset(offset) 
    # Only clef objects have an octaveChange field
    for elem in elems: 
        if elem.octaveChange is not None:
            part.replace(elem, newClef)
            return
    part.insert(offset, newClef)

def removeClef(offset, part): 
    """ Remove a clef from a given offset in a given part. """
    elems = getElementsByOffset(offset)
    for elem in elems: 
        # Only clef objects have an octaveChange field
        if elem.octaveChange is not None: 
            part.remove(elem)
            return

def insertMeasures(insertionOffset, part, insertedQLs): 
    """ Insert measures in a part by moving the offsets of 
        portions of the score by a given number of QLs. """
    part.shiftElements(insertedQLs, insertionOffset)
    # Broadcast whole file

def assignInstrument(part, instrumentStr): 
    """ Given an instrument name, assigns that instrument 
        to a part in the score. Each part can only have one
        instrument, so providing an offset isn't necessary. 
        The number of instruments supported on the backend
        are much to numerous to name."""
    instrument = music21.instrument.fromString(instrumentStr)
    elems = getElementsByOffset(0.0)
    for elem in elems: 
        if elem.instrumentName is not None: 
            part.replace(elem, instrument)
            return
    part.insert(0.0, instrument)

def addDynamic(offset, part, dynamicStr): 
    """ Adds a dynamic marking to a part at a given offset.
        Acceptable values of dynamicStr are 'ppp', 'pp', 'p',
        'mp', 'mf', 'f', 'ff', and 'fff'. """
    dyanmic = music21.dynamics.Dynamic(dynamicStr)
    elems = getElementsByOffset(offset) 
    for elem in elems: 
        if elem.volumeScalar is not None: 
            part.replace(elem, dynamic)
            return
    part.insert(offset, dynamic) 

def removeDynamic(offset, part): 
    """ Removes a dynamic marking from a part at a given offset. """
    elems = getElementsByOffset(offset) 
    for elem in elems: 
        if elem.volumeScalar is not None: 
            part.remove(elem)
            return

def addLyric(offset, part, lyric): 
    """ Add lyrics to a given note in the score. """
    notes = part.notes
    for note in notes: 
        if note.offset == offset: 
            note.addLyric(lyric)
            # Broadcast success
            return
    # Broadcast failure
