# Client Architecture

[Back](index.md)

[Up](../index.md)

A Composte client is an application that facilitates the process of interacting
with a Composte server and using the services provided. Composte clients act
primarily as a collaborative sheet music editor, in the same way that Google
Docs serves as collaborative document editor.

The provided Composte client uses a GUI created with PyQt.

## Core features

Clients have _at least_ the following responsibilities:

* View projects and project metadata
* Select a project to work on
* Edit the current project
* Merge authoritative updates into the current project, overwriting any
  client-side-cached changes that would conflict.
* Allow playback of the current project
* Export the sheet music for the current project
* Facilitate user registration and login to the server
* Facilitate permissions management for projects

## Other features

These features are not strictly part of the minimum deliverable, but
contribute greatly to a good user experience.

* Connect to a configurable remote server
* Load custom sound fonts

## Modules

Note that some modules are shared between the client and server.

__Login/Landing Page GUI__

The Composte client uses a GUI to manage server login and opening projects.

__Sheet Music Editor GUI__

The Composte client is a Python program and uses a GUI to drive
interaction with the user.

__Diff Producer/Processor__

Updates are exchanged via diffs, which are hard. Therefore it is probably
a good idea to abstract those away.

__Network__

Since the client probably communicates with the server over a network, the
client had best have the capability to communicate over a network. A
message queue such as ØMQ may suffice.

__Music Things__

If this is Google Docs for Music, it had best be ablt to do some music
things.

__Host Interactions (Playback, export, etc.)__

At the very least, we would like to provide playback capabilities and the
ability to export the created sheet music to a file. It may turn out that
`music21` has these features (or appropriate delegation strategies)
built-in, but we'll plan for the worst.

__Cache (Soundfonts, etc.)__

If ever the client needs to cache things like soundfonts, it would be best
to have a simple caching delegate to make use of.

__Serializer/Deserializer__

Because this isn't Erlang, communication is done using textual/binary
messages, and there is no built-in serialization for arbitrary Python
objects. Thus a project-standard serialization/deserialzation suite is
necessary.

