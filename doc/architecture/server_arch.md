# Server Architecture

[Back](index.md)

[Up](../index.md)

A Composte server is an application representing a node that allows multiple
clients to collaborate on projects. Composte servers are independent and,
semantically, there is no centralized server registry or tiering of servers as
in DNS.

Composte servers independently manage stores of users and projects.

## Core features

Servers have _at least_ the following responsibilities:

* Authentication of users
* Allow creation of projects
* Allow users to add collaborators to projects they own
* Allow updates to projects and their metadata
* Allow project collaborators to push updates to the same project concurrently
* Track client connections' associations with current projects
* Periodically push authoritative updates to clients
* Apply updates to projects atomically

## Other features

These features are not strictly part of the minimum deliverable, but
contribute greatly to a good user experience.

## Modules

This is a tentative, untiered breakdown of the modules that are required for
the operation of this reference implementation of a Composte server

Note that some modules are shared between the client and server.

__Authentication__

Servers keep auth databases to map `username` -> `salted password hash`, but
clearly some sort of cryptographic hashing and salting is required.

__Database__

We have at least the following tables to manage:

* Authentication table
    * { Username (Primary key), salt, salted password hash }
* Project Table
    * { UUID (Primary key), filepath or blob }

Things this module will have to do:

* Provide a usable wrapper around database clients
* Provide some defense against injection attacks

__Caching__

Regardless of where the projects themselves are stored, we would prefer not to
hit the backing store _every_ time an update to a project comes through, so a
caching layer should help performance.

Things this module will have to do:

* Periodically flush data to the disk/database
* Periodically flush and drop projects that have been inactive for some time
    * This implicitly covers projects where everyone is done working for the
      time
* Transparently fetch data from the database/disk
* Loosely limit the memory that active projects take up in memory (?)

__Filesystem Interactions__

Since files will be lying bare on the filesystem, it may be a good idea to
abstract that interaction away.

Things this modules will have to do:

* Stop us from accidentally doing bad things to the filesystem
* Perhaps enforce a storage quota

__Broadcasts__

The server must periodically broadcast updates to connected clients, relative
to the projects that they are each editing. By periodically, we mean each time
a client update message is accepted.

Sending messages is annoying and potentially racy.

Things this module will have to do:

* Provide a monitor pattern protecting the action of sending broadcasts

__Diff Producer/Processor__

Updates are exchanged via diffs, which are hard. Therefore it is probably a
good idea to abstract those away.

Things this module will have to do:

* Produce diffs
* Merge diffs into a project

__Music Things__

If this is Google Docs for Music, it had best be able to do some music things.

Things this module will have to do:

* Music things

__Websocket Server__

Since the server probably communicates over websockets, it had best have a
websocket server to communicate with.

Things this module will have to do:

* Manage connections and handles

__Serializers/Deserializer__

Because this isn't Erlang, communication is done using textual/binary
messages, and there is no built-in serialization for arbitrary Python objects.
Thus a project-standard serialization/deserialzation suite is necessary.

Things this module will have to do:

* Serialize things
* Deserialize things

__Easter Eggs__

Spontaneous features

