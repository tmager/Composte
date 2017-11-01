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
* Allow updates to projects and their metadata
* Allow project collaborators to push updates to the same project concurrently
* Track client connections' associations with current projects
* Periodically push authoritative updates to clients
* Apply updates to projects atomically

## Other features

These features are not strictly part of the minimum deliverable, but
contribute greatly to a good user experience.

## Modules

Tentative breakdown, untiered

Note that some modules are shared between the client and server.

Authentication
    Servers keep auth databases to map (Username , Password) -> UserID, but
    clearly some sort of cryptographic hashing and salting is required.

Database
    We have at least an authentication table, and perhaps tables for projects
    too.

Caching
    Regardless of where the projects themselves are stored, we would prefer
    not to hit the backing store _every_ time an update to a project comes
    through, so a caching layer should help performance.

Filesystem Interactions (?)
    If it turns out that we end up having files lying bare on the filesystem,
    it may be a good idea to abstract those interactions away.

Broadcasts
    The server must periodically broadcast updates to connected clients,
    relative to the projects that they are each editing.

Diff Producer/Processor
    Updates are exchanged via diffs, which are hard. Therefore it is probably
    a good idea to abstract those away.

Music Things
    If this is Google Docs for Music, it had best be able to do some music
    things.

Websocket Server
    Since the server probably communicates over websockets, it had best have a
    websocket server to communicate with.

Serializers/Deserializer
    Because this isn't Erlang, communication is done using textual/binary
    messages, and there is no built-in serialization for arbitrary Python
    objects. Thus a project-standard serialization/deserialzation suite is
    necessary.

