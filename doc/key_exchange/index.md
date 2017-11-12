# Key Exchange

[Up](../index.md)

Because this version of the ØMQ protocol does not support a secure, encrypted
mode, we must provide our own secure encryption on top of ØMQ. We do this by
piggybacking off of HTTPS to exchange keys. Because we then have two distinct
connections that we must associate, attribution/proof of identity also becomes
an issue.

The procedure for key exchange is roughly as follows:

1. The client makes an HTTPS request to the server, asking for a key
2. The server responds with an AES-128 key
3. Any messages that the client the sends to the server must be preceded by
   the key, encrypted using the server's public key

Thus the encryption key provided to the client also serves as a proof of
identity.

