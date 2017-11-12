import music21

# The server always needs to know WHERE to make 
# an update, and needs to send that information 
# to all connected clients. Thus, the offset from
# the beginning of the piece (in quarterLengths, or "qLs")
# must always be given as the first argument to all
# update functions. Also, the server must know WHICH 
# stream to apply the update in, hence the need to
# pass it as the second argument in all cases.

def changeKeySig(offset, stream, newKeySig): 
    """ Changes the Key Signature at a given offset inside a stream """
    oldKeySigs = stream.getKeySignatures()
    for i in range(len(oldKeySigs)): 
        if oldKeySigs[i].offset == offset: 
            stream.replace(oldKeySigs[i], newKeySig)
            if i + 1 == len(oldKeySigs): 
                renameNotes(offset, stream, newKeySig)
            else: 
                renameNotes(offset, stream, newKeySig, oldKeySigs[i + 1].offset)
            # Broadcast the whole file 
            return
    stream.insert(offset, newKeySig)
    for oldKeySig in oldKeySigs: 
        if offset < oldKeySig.offset: 
            renameNotes(offset, stream, newKeySig, oldKeySig.offset) 
            # Broadcast the whole file 
            return
    renameNotes(offset, stream, newKeySig)
    # Broadcast the whole file
  
def renameNotes(startOffset, stream, keySig, endOffset=None):
    """ Rename all notes affected by a key signature change
        intelligently so as to not have sharp accidentals
        in a flat key signature. Diffs need to accumulate 
        while the renaming is in process. """
    notes = stream.notes
    hasSharps = 0 < keySig.sharps 
    for note in notes: 
        offset = note.offset
        if endOffset is None: 
            if startOffset <= offset: 
                note = renameNote(note, hasSharps)
        else: 
            if startOffset <= offset and offset <= endOffset:
                note = renameNote(note, hasSharps)

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
                
def changeTimeSig(offset, stream, newTimeSig): 
    """ Changes the Time Signature at a given offset inside a stream """
    oldTimeSigs = stream.getTimeSignatures()
    for oldTimeSig in timeSigs: 
        if oldTimeSig.offset == offset: 
            stream.replace(oldTimeSig, newTimeSig)
            # Broadcast
    stream.insert(offset, newTimeSig)
    # Broadcast

def insertNote(offset, stream, newNote): 
    """ Add a note at a given offset to a stream. """
    notes = stream.notes
    for note in notes: 
        if note.offset == offset: 
            note.add(newNote)
            # Broadcast
    stream.insert(offset, music21.chord.Chord(newNote.name)) 
    # Broadcast

def appendNote(stream, newNote): 
    """ Add a note at the end of a stream. """
    stream.append(music21.chord.Chord(newNote))
    # Broadcast

def removeNote(offset, stream, removedNoteName): 
    """ Remove a note at a given offset into a stream. """
    notes = stream.notes
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
        and a duration in quarter lengths. 
        Transparently converts all notes to chords
        for ease of manipulation at later times. """
    note = music21.note.Note(pitchName)
    note.duration = durationInQLs
    chord = music21.chord.Chord(note)
    return chord

def addLyric(offset, stream, lyric): 
""" Add lyrics to a given note in the score. """
    notes = stream.notes
    for note in notes: 
        if note.offset == offset: 
            note.addLyric(lyric)
            # Broadcast success
            return
    # Broadcast failure
