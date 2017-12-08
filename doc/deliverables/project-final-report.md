# COMP 50CP Final Project Report

## Composte

Make bad music together

### Team

Export-By-Email

* Tom Magerlein
* Robert Goodfellow
* Wesley Wei

### What is Composte?

Composte is an application that allows collaborators to concurrently
collaborate on music composition. Think of it as Google Docs for music, but
bad.

### This submission

This submission can do/supports the following:

* Multiple concurrent users working on projects
* Display notes
* Edit notes
* Change MIDI instrument
* MIDI instrument change
* Accidentals
* Automatic Treble Clef
* Set Tempo
* Project-local chat/text-to-speech
* Impoverished scripting language
* More impoverished scripting language

### Design/Architecture

<img src="finalClassDiagram.jpg"></img>

Composte builds a simple RPC to separate servers from clients. This RPC is
built on top of several modules, described below.

__auth__

Authentication of username/password pairs.

__database__

Encapsulation of database interactions.

__protocol__

Encapsulates serialization and deserialization of messages.

__util__

A collection of miscellaneous utilities, including music handling and a
generic REPL.

__network__

Encapsulates communicating over a network.

&nbsp;

The music processing backend processes music.

__util__

The music processing backend is implemented entirely with music21, a
music processing engine developed at MIT. A thin wrapper around the
music manipulation functions was necessary in order to perform the
RPC calls intelligently. Playback is indirectly handled by music21,
which delegates to pygame, which attempts to delegate to a combination
of timidity and freepats.

&nbsp;

The GUI

The primary developer has declined to comment.

### Outcome

Somehow, it appears to work.

Alternatively, we have two impoverished REPLs driving a GUI and interactions
with a remote server.

&lt;/sarcasm&gt;

### Looking back at our design

Our design at its core has three somewhat disjoint tasks: Maintaining and
mutating an internal representation of music, GUI-driven collection of changes
to music (Actually REPL-driven), and remote procedure call (RPC).

While we still believe that this model is fairly elegant and practical, we see
many flaws in our implementations of the modules backing these tasks.

The most prominent lesson we learned was that GUI development is difficult and
time-consuming. While there are plenty of powerful, well-documented GUI
toolkits out there for Python, we didn't find anything aimed at providing a
sheet music editor. In this sense we failed to foresee how much of a pain
developing the GUI would be, given that none of us have experience developing
a GUI of this nature. It turns out that making an interactive graphical editor
is hard.

Therefore, we fell back to driving the client primarily with a terminal-based
REPL. This reduced the amount of GUI work that was required for us to both
test and use our application. While text driven interaction is the antithesis
of a graphical music editor, we believe that it is still ultimately useful, as
a scriptable interface is always a nice feature. To be clear, we believe a
full blown GUI is important, but we also believe that we have neither the time
nor the expertise to pull one off in the 7 hours before the demo.

The internal representation of music, is sadly not cleanly separated from the
GUI. In order to slightly reduce the amount and magnitude of headaches Tom
had, is having, and will continue to have, the internal representation of
music is somewhat tailored to the graphical features that we would like the
GUI to have.

When attempting to integrate the GUI with the music backend, several
deficiencies in the design of the backed were discovered. Firstly, because
rests have no direct representation (they are the absence of notes at some
point in the score), the GUI has no point of reference to allow it draw rests.
Furthermore, there is no backend concept of measures whatsoever; they are a
fiction imposed by the GUI. This made Tom sad. This also created the need for
an entire extra layer of abstraction within the GUI's structure. Lastly, the
playback engine can only play one stream at a time, and because music21
streams are composable (as in function composition), if a score were modelled
as a stream of streams rather than a list of streams, it would be possible to
play back all parts at once and it would make more sense semantically.

The way communication over the network is implemented under our RPC is
somewhat unsatisfying. Because we chose to collect all incoming client
messages into a single REQ/REP ØMQ socket, we do not have the notion of
separate connections. This hurts us in two ways: only one message can be
processed at a time on the server, and broadcasts go out to _all_ connected
clients, not just the ones subscribed to the project of interest. A better
underlying network model would have the concept of separate connections, as
that would allow both concurrent processing of unrelated messages and the
restriction of broadcasts to the clients that it is intended for. A migration
away from the REQ/REP network model is warranted, but discovered late enough
to prove challenging to change without pushing us past the deadline.

This means that currently, most concurrency issues in this application do not
have to do with the server processing messages from clients. This will
hopefully change in future releases.

In the face of how glaringly _bad_ the network model is, we have found the
actual network endpoints to be surprisingly pleasant to use.

### Division of Labor

Tom Magerlein:
* GUI
* Debug console

Robert Goodfellow
* Internal representation of music
* Diff handling

Wesley Wei
* RPC
* Deployment/Official server
* Generic REPL

Unfortunately, we did not dedicate sufficient time to documentation to produce
documentation of acceptable quality. Much of the documentation we have is out
of date and no longer correct.

### Bug/Spontaneous Feature Tracker

<!--
* Python references are _fun_ (sarcasm)
    * Single updates to projects were causing serverside failures involving
      what appeared to be a double-insertion in a single function call.
    * Because all "nonprimitive" objects in Python are mutable, extracting
      parts of projects and mutating those to produce a diff has the side
      effect of also applying the mutation to the project's contents.
      Attempting to apply the generated diff to the project later then causes
      a double update, because the desired operation _has already been
      performed_ on the project.

* Message loss
    * Clients and servers could communicate when run on the same host, but
      failed to communicate whenever the server was run on a remote VPS.
    * What we thought it was: Messages being dropped for some mysterious
      reason.
    * The actual problem: The VPS service provider blocked the ports we
      originally intended to use: 6666 and 6667. This is likely due to port
      6666 being commonly used by trojans, and irc using 6666 and 6667.
      Running an irc service is against the provider's TOS. Ports 6660 to 6670
      were blocked.
    * Solved by defaulting to port 5000 and 5001 instead.

* Boundary conditions
    * When replacing metronome marks, the music21 backend special cases the
      metronome mark at the very beginning. It is a default value and is not
      actually present to be replaced. For this reason, replacing the
      metronome mark at the beginning of a part is in fact an insertion
      operation.
-->

* Backend ties don't work in playback
    * Ties, though not represented on the GUI, can still exist in the internal
      representation. Unfortunately they are not respected when performing
      playback of music.
    * We have determined that this is a bug underneath the `music21` package
      that we use to do playback. We have submitted a ticket.
    * See [this issue](https://github.com/cuthbertLab/music21/issues/266)

## Source Code Tourist's Guide

For your viewing pleasure or displeasure, we provide an elided `tree` of the
repository.

    Composte
    ├── auth
    │   └── auth.py
    ├── client
    │   └── < GUI Suffering >
    ├── ComposteClient.py
    ├── ComposteServer.py
    ├── data
    │   ├── composte.db
    │   └── users
    │       └── < User data >
    ├── database
    │   └── driver.py
    ├── demoScripts
    │   └── < Demonstration scripts >
    ├── doc
    │   ├── architecture
    │   │   └── index.md
    │   ├── deliverables
    │   │   └── index.md
    │   ├── images
    │   │   └── Bad_Diagrams
    │   │       └── < "Diagrams" >
    │   ├── index.md
    │   └── protocol
    │       └── index.md
    ├── Dockerfile
    ├── html
    │   ├── index.html
    │   └── styles
    │       └── composte.css
    ├── logs
    │   └── < Logs >
    ├── network
    │   ├── base
    │   │   ├── exceptions.py
    │   │   ├── handler.py
    │   │   └── loggable.py
    │   ├── client.py
    │   ├── conf
    │   │   ├── logging.conf
    │   │   └── logging.py
    │   ├── dns.py
    │   ├── fake
    │   │   └── security.py
    │   └── server.py
    ├── protocol
    │   ├── base
    │   │   └── exceptions.py
    │   ├── client.py
    │   └── server.py
    ├── README.md
    ├── requirements.txt
    └── util
        ├── bookkeeping.py
        ├── classExceptions.py
        ├── composteProject.py
        ├── misc.py
        ├── musicFuns.py
        ├── musicWrapper.py
        ├── repl.py
        └── timer.py

## Source Descriptions

__Top Level__

`ComposteServer.py` implements a complete Composte server on top of the
network server.

`ComposteClient.py` implements most of a Composte client on top of the network
client.

__auth__

`auth.py` contains functions to create and verify password hashes.

__database__

`driver.py` encapsulates access to the the database. It translates between
database schemas and python objects.

__network__

`client.py` provides a network client.

`server.py` provides a network server.

`dns.py` provides methods to get ip addresses from domain names.

__network/base__

`exceptions.py` contains exceptions the network clients and servers expect
users to raise in the event of trouble.

`handler.py` provides a base class for a stateful message handler. Users may
choose to derive their message handlers from this.

`loggable.py` provides a base class to provide simpler logging.

__network/fake__

`security.py` provides classes conforming to the `encryption_scheme` interface
that the network servers and clients expect, but provide no encryption.

__network/conf__

`logging.py` contains the default logging configuration that the network
clients and servers use, as well as a method to read that configuration.

__client__

This module contains the GUI.

__doc__

This directory contains documentation of the project and deliverables for
COMP 50CP. Much of the documentation is out of date, and a fair amount may
also be unreachable from internal links.

__protocol__

`client.py` contains methods for serializing and deserializing client
messages.

`server.py` contains methods for serializing and deserializing server
messages.

__protocol/base__

`exceptions.py` contains exceptions that the `protocol` module may raise.

__util__

The `util` module implements a number of miscellaneous things that are needed
to make the server work. Notably, the music backend is implemented here

`bookkeeping.py` implements two static object pools.

`classExceptions.py` provides some exceptions used in the class hierarchy used
by the GUI.

`composteProject.py` provides the internal, in-memory representation of a
project. This also provides serialization and deserialization facilities.

`misc.py` provides a function to get the version (commit) hash.

`musicFuns.py` provides the mutators for the internal representation of music.

`musicWrapper.py` provides a thin wrapper around `musicFuns.py`, conforming to
the message handler contracts that `ComposteServer` expects.

`timer.py` provides a method to run a function at a configurably approximate
interval.

`repl.py` provides the REPL shell/scripting interface that Composte has
decomposed into. The REPL is likely to have access to all methods that the GUI
exposes to the user, and indeed may have finer-grained access to music
manipulation methods. The REPL is feature-impoverished, but capable of just
enough to be semi-useful.

