# Composte
## Get together to make bad music

For even worse documentation, see [docs](doc/index.md).

## Getting Composte

In general, you can fetch the lastest stable version from here:

    git clone https://github.com/tmager/Composte.git

Occasionally, you may find that the server you are connecting to uses a
different version, and you will have to obtain a client of that version. One
of these days we'll figure out how you can do that.

## Building and Running

The Composte client and server provided here are `python3` applications and do
not require compilation.

General setup:

    pip install -r requirements.txt

If you will be relying on systemwide packages, refer to `requirements.txt` for
a list of python packages that are required.

In general, you shouldn't be starting Composte servers manually. It is
recommended that you run it as a service.

To start a Composte server:

    server.py

To start a Composte client:

    client_main.py

