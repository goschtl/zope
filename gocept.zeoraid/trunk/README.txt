================
ZEO RAID storage
================

The ZEO RAID storage is a storage intended to make ZEO installations more
reliable by applying techniques as used in harddisk RAID solutions.

The implementation is intended to make use of as much existing infrastructure
as possible and provide a seamless and simple experience on setting up a
reliable ZEO server infrastructure.

Note: We use typical RAID terms to describe the behaviour of this system.

The RAID storage
================

The ZEO RAID storage is a proxy storage that works like a RAID controller by
creating a redundant array of ZEO servers. The redundancy is similar to RAID
level 1 except that each ZEO server keeps a complete copy of the database.

Therefore, up to N-1 out of N ZEO servers can fail without interrupting.

It is intended that any storage can be used as a backend storage for a RAID
storage, although typically a ClientStorage will be the direct backend.

The ZEO RAID server
===================

The RAID storage could (in theory) be used directly from a Zope server.
However, to achieve real reliability, the RAID has to run as a storage for
multiple Zope servers, like a normal ZEO setup does.

For this, we leverage the normal ZEO server implementation and simply use a
RAID storage instead of a FileStorage. The system architecture looks like
this::

    [ ZEO 1 ]     [ ZEO 2 ]   ...   [ ZEO N ]
               \       |       /
                \      |      /
                 \     |     /
                  \    |    /
                   \   |   /
                    \  |  /
                  [ ZEO RAID ]
                    /  |  \
                   /   |   \
                  /    |    \
                 /     |     \
                /      |      \
               /       |       \
    [ Zope 1 ]    [ Zope 2 ]  ...   [ Zope N]

ZEO RAID servers maintain a list of all the optimal, degraded and recovering
storages and provide an extended ZEO rpc API to allow querying the RAID status
and disabling and recovering storages at runtime.

Making the RAID server reliable
===============================

The RAID server itself remains the last single point of failure in the system.
This problem is solved as the RAID server does not maintain any persistent
state (except the configuration data: it's listening ip and port and the list
of storages).

The RAID server can be made reliable by providing a hot-spare server using
existing HA tools (taking over the IP when a host goes down) and the existing
ZEO ClientStorage behaviour.

The RAID server is capable of deriving the status of all storages after
startup so the hot-spare server does not have to get updated information
before switching on. One drawback here: if all storages become corrupt at the
same time, the RAID server will happily pick up the storage with the newest
last transaction and use it as the optimal storage.

To avoid this, we'd have to create a well known OID (os something similar) to
annotate a storage with its status. This would mean that storages would have
to be initialized as a RAID backend though and can't be easily migrated.

Development
===========

A mailing list is available at `zeoraid@lists.gocept.com`. Send an email with
the subject `subscribe` to this address to join the list.

A bug tracker is available at launchpad:
https://bugs.launchpad.net/gocept.zeoraid/
