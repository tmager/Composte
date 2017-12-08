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
* MIDI playback
* Set time signature
* Set/Change key signature
* Accidentals
* Automatic Treble Clef
* Set Tempo
* Triplets
* Impoverished scripting language
* More impoverished scripting language

### Design/Architecture

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

### Outcome

We have an impoverished REPL driving a GUI and interactions with a remote
server.

### Looking back at our design

Our design at its core has three somewhat disjoint tasks: Maintaining and
mutating an internal representation of music, GUI-driven collection of changes
to music, and remote procedure call (RPC).

While we still believe that this model is fairly elegant and practical, we see
many flaws in our implementations of the modules backing backing these tasks.

The most prominent lesson we learned was that GUI development is difficult and
time-consuming. While there are plenty of powerful, well-documented GUI
toolkits out there for Python, we didn't find anything aimed at providing a
music note editor. In this sense we failed to foresee how much of a pain
developing the GUI would be, given that none of us have experience developing
a GUI of this nature. It turns out that making an interactive graphical editor
is hard.

Therefore, we fell back to driving the client primarily with a terminal-based
REPL. This reduced the amount of GUI work that was required for us to both
test and use our application. While text driven interaction is the antithesis
of a graphical music editor, we believe that it is still ultimately useful, as
a scriptable interface is always a nice feature. To be clear, we believe a
full blown GUI is important, but we also believe that we have neither the time
nor the expertise to pull one off in the limited time that we have.

The internal representation of music, sadly is not cleanly separated from the
GUI. In order to slightly reduce the amount and magnitude of headaches Tom
had, is having, and will continue to have, the internal representation of
music is somewhat tailored to the graphical features that we would like the
GUI to have.

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

### Division of Labor

Tom Magerlein:
* GUI
* Diff handling
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

* Backend ties don't work in playback
    * Ties, though not represented on the GUI, can still exist in the internal
      representation. Unfortunately they are not respected when performing
      playback of music.
    * We have determined that this is a bug underneath the `music21` package
      that we use to do playback. We have submitted a ticket.

### Code breakdown

(Duplicate from README before submitting)

