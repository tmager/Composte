# Composte Objects

[Back](index.md)

[Up](../index.md)

# Objects

Composte offers users the ability to collaborate on projects.

## Software Objects

### Users

Users are identified by their usernames, which must be unique within any
single Composte server.

Users also have cookies associated with any active connections that they own.

```python
    class User:
        __username = str()
        __cookies = []
```

### Projects

Projects are uniquely identified by a UUID. Projects also contain metadata,
including but not limited to the following:

* Owner
* Collaborators
* Creation date
* Time of last edit
* Title
* Subtitle
* Composer
* Lyricist

Projects must also contain, somewhat obviously, the sequence of notes that
make up the actual content of the project.

Canonical metadata, such as owner, title, composer, etc can have their own
fields, but any optional metadata will require a generic container.

```python
    class Project:
        __title = str()
        __subtitle = str()
        __composer = str()
        __owner = str()
        __collaborators = str()

        # Probably whatever music21 uses, but we may have to wrap it
        # Either way it'll probably be more list-like than anything else
        __notes = []
```

## Data Objects
All data objects are modeled by a music21 object, and 
also have corresponding graphical assets that are displayed by the GUI.

### Notes
music21 Note objects have many properties, but most important are
pitch and duration. The pitch is necessary to know what staff line 
to draw the note asset on, and the duration is necessary to know which 
note asset to draw.

### Rests
music21 Rests are simply notes without pitch attached to them, meaning
they only have duration. Just as with notes, the duration must be 
known in order to draw the correct asset on the GUI.

### Key Signatures
music21 KeySignature objects keep track of how many sharps and flats 
are in the current key signature. Because there are finitely many 
possible key signatures, each one gets its own asset. 

### Time Signatures
music21 TimeSignatures keep track of how many quarter note
durations are in a single measure of music. This is represented
graphically by a small number of time signature assets, but 
since the time signature also indicates barline/measure divisions, 
the GUI needs to keep track of the underlying time signature object
in order to draw the correct number of beats in a given measure. 
