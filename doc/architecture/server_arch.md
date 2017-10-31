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
* Alow project collaborators to push updates to the same project concurrently
* Track client connections' associations with current projects
* Periodically push authoritative updates to clients
* Apply updates to projects atomically

## Other features

