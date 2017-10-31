# Client Architecture

[Back](index.md)
[Up](../index.md)

A Compste client is an application that facilitates the process of interacting
with a Composte Server and using the services provided. Composte clients act
primarily as a collaborative sheet music editor in the same sense that Google
Docs serve as collaborative document editors.

## Core features

Clients have _at least_ the following responsibilities:

* Connect to a configurable remote server
* View projects and project metadata
* Select a project to work on
* Allow playback from the current project
* Edit the current project
* Merge authoritative updates into the current project, overwriting any
  clientside-cached changes that would conflict.


## Other features

