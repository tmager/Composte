# Protocol Overview

[Back](index.md)

[Up](../index.md)

This document does _not_ describe the particulars of what messages in the
Composte protocol look like. Instead, it describes the semantic meanings of
messages exchanged between clients and servers.

The Composte protocol must support all possible communications between clients
and servers. To help us all get a feel for what capabilities are needed, some
example message types are listed below.

Error conditions listed here are serverside. Implementers may wish to hide
some of the specifics of error conditions from clients to avoid leaking
information.

The message initiator is listed first.

## Server -> Client

* `SPOT Update`

## Client -> Server

* `Register`
* `Login`
* `Create`
* `Share`
* `Subscribe`
* `Update`
* `Unbscribe`

## Details

### `SPOT Update`

This is a __server initiated__ message

The server (a Single Point Of Truth, or SPOT) periodically broadcasts an 
authoritative update to all clients currently editing projects.

__Sent:__

A diff capturing the updates that the server applied since the last update was
broadcast.

__Expected Response:__

None

__Errors:__

There should be none but those induced by network conditions.

### `Register`

This is a __client initiated__ message

Clients must register with a _unique_ username and a 
password in order to gain access to projects. 

__Sent:__

Login credentials: Username, password

__Expected Response:__

Success, a session cookie, and a list of shared Projects

__Errors:__

Naught but the network

### `Login`

This is a __client initiated__ message

Clients must authenticate in order to gain access to projects. 

__Sent:__

Login credentials: Username, password

__Expected Response:__

Success, a session cookie, and a list of shared projects

__Errors:__

Authentication Failure

### `Create`

This is a __client initiated__ message

Users must be able to create projects.

TODO - It is not clear at this time what partial descriptions of projects are
required for project creation, but a unique project ID will be necessary
at the very least.

__Sent:__

Project name, owner and shared editors, extra metadata (?)

__Expected Response:__

Success, project ID, blank project

__Errors:__

Invalid/Unknown User

### `Subscribe`

This is a __client initiated__ message

Users must be able to subscribe to projects in order to get
a live feed of edits from the server.

__Sent:__

UserID, ProjectID

__Expected Response:__

Success, project state

__Errors:__

* Unknown project
* Unknown user
* User does not have permission to edit project

### `Update`

This is a __client initiated__ message

Users must be able to make changes to the project.

Note that it is possible for a race to happen when conflicting updates are
sent to the server in between authoritative broadcasts. When such a race is
detected, one update wins at the discretion of the server and the others are
rejected either in part or in whole.

__Sent:__

A diff capturing the edits that the user has made since the last SPOT update

__Expected Response:__

Success

__Errors:__

Race detected, changes dropped

### `Unsubscribe`

This is a __client initiated__ message

Users must be able to unsubscribe from server
updates when finished with editing a project.

__Sent:__

UserID, ProjectID

__Expected Response:__

Success

__Errors:__

* Unknown user
* Unknown project
* User was not editing project
* User does not have permission to edit project

