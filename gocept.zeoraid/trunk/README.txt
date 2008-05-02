===============
ZEORaid storage
===============

The ZEORaid storage is a storage intended to make ZEO installations more
reliable by applying techniques as used in hard disk RAID solutions.

The implementation is intended to make use of as much existing infrastructure
as possible and provide a seamless and simple experience on setting up a
reliable ZEO server infrastructure.

Note: We use typical RAID terms to describe the behaviour of this system.

The RAID storage
================

The ZEORaid storage is a proxy storage that works like a RAID controller by
creating a redundant array of ZEO servers. The redundancy is similar to RAID
level 1.

Therefore, up to N-1 out of N ZEO servers can fail without interrupting
the service.

It is intended that any storage can be used as a backend storage for a RAID
storage, although typically a ClientStorage will be the direct backend.

The ZEORaid server
==================

The RAID storage could (in theory) be used directly from a Zope server.
However, to achieve real reliability, the RAID has to run as a storage for
multiple Zope servers, like a normal ZEO setup does.

For this, we leverage the normal ZEO server implementation and simply use a
RAID storage instead of a FileStorage. To achieve full reliability, you can
install multiple ZEORaid servers with identical configuration::

    [ Zope 1 ]                      [ ZEORaid 1 ]                  [ ZEO 1 ]
    [ Zope 2 ]    talk to all -->   [ ZEORaid 2 ]   talk to all -> [ ZEO 2 ]
    ...                             ...                            ...
    [ Zope N]                       [ ZEORaid N ]                  [ ZEO N ]


ZEO RAID servers maintain a list of all the optimal, degraded and recovering
storages and provide an extended Storage API to allow querying the RAID status
and disabling and recovering storages at runtime.

Development
===========

A mailing list is available at `zeoraid@lists.gocept.com`. Send an email with
the subject `subscribe` to this address to join the list.

A bug tracker is available at launchpad:
https://bugs.launchpad.net/gocept.zeoraid/
