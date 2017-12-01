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
* Landing screen to choose projects from [1]
* Display notes
* Edit notes
* MIDI playback [1]
* Update Metadata [1]
* Set time signature
* Set/Change key signature
* Accidentals
* Automatic Treble Clef
* Set Tempo
* Triplets

[1]: Not yet

Other facets of Composte, not necessarily user-facing features

* Protocol over ØMQ
* Per server serverside user registry (Username -> Password)
    * Usernames must be unique per server

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

A collection of miscellaneous utilities, including music handling.

__network__

Encapsulates communicating over a network.

### Outcome

We hope it works.

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
restriction of broadcasts to the clients that it is intended for.

### Division of Labor

Tom Magerlein:
* GUI
* Diff handling

Robert Goodfellow
* Internal representation of music
* Diff handling

Wesley Wei
* RPC
* Deployment/Official server

Unfortunately, we did not dedicate sufficient time to documentation to produce
documentation of acceptable quality. Much of the documentation we have is
likely to be out of date and no longer correct.

### Bug/Spontaneous Feature Tracker

* Clients would drop messages if more than one came between the polling cycles
    * A statement to store messages was placed outside of a loop, causing all
      messages but the last to be dropped
    * Fixed by moving the statement inside the loop

* Multiple deadlocks
    * Careless acquisition of locks frequently caused deadlock
    * Fixed by being more careful about lock acquisition

* Database deadlock
    * The database would be observed to be locked after a failed integrity
      check
    * Solved by not failing the integrity check

* Message loss
    * Clients and servers could communicate when run on the same host, but
      failed to communicate whenever the server was run on a remote VPS.
    * The actual problem: the VPS service provider blocked the port we
      originally intended to use: 6666 and 6667. This is likely due to port
      6666 being commonly used by trojans, and irc using 6666 and 6667.
      Running an irc service is against the provider's TOS. Ports 6660 to 6670
      were blocked.
    * Solved by defaulting to port 5000 and 5001 instead.

### Code breakdown

(Duplicate from README before submitting)

