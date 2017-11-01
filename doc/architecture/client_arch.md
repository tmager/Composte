# Client Architecture

[Back](index.md)

[Up](../index.md)

A Compste client is an application that facilitates the process of interacting
with a Composte Server and using the services provided. Composte clients act
primarily as a collaborative sheet music editor in the same sense that Google
Docs serve as collaborative document editors.



## Core features

Clients have _at least_ the following responsibilities:

* View projects and project metadata
* Select a project to work on
* Allow playback from the current project
* Edit the current project
* Merge authoritative updates into the current project, overwriting any
  clientside-cached changes that would conflict.

## Other features

These features are not strictly part of the minimum deliverable, but
contribute greatly to a good user experience.

* Connect to a configurable remote server

## Modules

Tentative breakdown, untiered

Note that some modules are shared between the client and server.

GUI
    The Composte client is a Python program and uses a GUI to drive
    interaction with the user.

Diff Producer/Processor
    Updates are exchanged via diffs, which are hard. Therefore it is probably
    a good idea to abstract those away

Websocket Client
    Since the client probably cocmmunicates over websockets, it had best have
    a websocket client to communicate with.

Music Things
    If this is Google Docs for Music, it had best be ablt to do some music
    things.

Host Interactions (Playback?, export, etc)
    At the very least, we would like to provide playback capabilities, if not
    export and other conveniences. It may turn out that `music21` has these
    features (or appropriate delegation strategies) built-in, but we'll plan
    for the worst.

Cache (Soundfonts, etc)
    If ever the client needs to cache things like soundfonts, it would be best
    to have a simple caching delegate to make use of.

Serializers/Deserializer
    Because this isn't Erlang, communication is done using textual/binary
    messages, and there is no built-in serialization for arbitrary Python
    objects. Thus a project-standard serialization/deserialzation suite is
    necessary.

