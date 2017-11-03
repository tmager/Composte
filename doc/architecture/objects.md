# Composte Objects

[Back](index.md)

[Up](../index.md)

# Objects

Composte offers users the ability to collaborate on projects.

## Users

Users are identified by their usernames, which must be unique within any
single Composte server.

Users also have cookies associated with any active connections that they own.

```python
    class User:
        __username = str()
        __cookies = []
```

## Projects

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

