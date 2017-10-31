# Protocol Overview

[Up](../index.md)

This document does _not_ describe the particulars of what messages in the
Composte protocol look like. Instead, it describes the semantic meanings of
messages exchanged betwene clients and servers.

The Composte protocol must support all possible communications between clients
and servers. To help us all get a feel for what capabilities are needed, some
example message types are listed below.

The initiator is listed first.

## Server -> Client

* `Authoritative Update`

## Client -> Server

* `Login`
* `Create Project`
* `Begin Editing`/`Select Project`
* `Propose Update`
* `Done Editing`/`Close Project`

## Details

### `Authoritative Update`

This is a __server initiated__ message

The server periodically broadcasts an authoritative update to all clients
currently editing projects.

__Sent:__

A diff capturing the updates that the server applied since the last update was
broadcast.

__Expected Response:__

None

__Errors:__

I hope not

### `Login`

This is a __client initiated__ message

Clients must authenticate in order to gain access to projects.

__Sent:__

Login credentials: Username, password

__Expected Response:__

Success, Project listings and metadata

__Errors:__

Authentication Failure

### `Create Project`

This is a __client initiated__ message

Users must be able to create projects

__Sent:__



__Expected Response:__



__Errors:__



### `Begin Editing`/`Select Project`

This is a __client initiated__ message

Users must be able to select projects to edit

__Sent:__



__Expected Response:__



__Errors:__



### `Propose Update`

This is a __client initiated__ message

Users must be able to make changes to the project

__Sent:__



__Expected Response:__



__Errors:__



### `Done Editing`/`Close Project`

This is a __client initiated__ message

Users must be able to stop editing a project

__Sent:__



__Expected Response:__



__Errors:__



