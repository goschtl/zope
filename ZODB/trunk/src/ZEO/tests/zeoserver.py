##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Helper file used to launch a ZEO server cross platform"""

import os
import sys
import errno
import getopt
import random
import socket
import asyncore
import ThreadedAsync.LoopCallback

import ZConfig.Context
import zLOG
from ZODB import StorageConfig
import ZEO.StorageServer


def load_storage(fp):
    context = ZConfig.Context.Context()
    rootconf = context.loadFile(fp)
    storageconf = rootconf.getSection('Storage')
    return StorageConfig.createStorage(storageconf)


def cleanup(storage):
    # FileStorage and the Berkeley storages have this method, which deletes
    # all files and directories used by the storage.  This prevents @-files
    # from clogging up /tmp
    try:
        storage.cleanup()
    except AttributeError:
        pass


def log(label, msg, *args):
    zLOG.LOG(label, zLOG.DEBUG, msg % args)


class ZEOTestServer(asyncore.dispatcher):
    """A server for killing the whole process at the end of a test.

    The first time we connect to this server, we write an ack character down
    the socket.  The other end should block on a recv() of the socket so it
    can guarantee the server has started up before continuing on.

    The second connect to the port immediately exits the process, via
    os._exit(), without writing data on the socket.  It does close and clean
    up the storage first.  The other end will get the empty string from its
    recv() which will be enough to tell it that the server has exited.

    I think this should prevent us from ever getting a legitimate addr-in-use
    error.
    """
    __super_init = asyncore.dispatcher.__init__

    def __init__(self, addr, storage, keep):
        self.__super_init()
        self._storage = storage
        self._keep = keep
        # Count down to zero, the number of connects
        self._count = 1
        # For zLOG
        self._label ='zeoserver:%d @ %s' % (os.getpid(), addr)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # Some ZEO tests attempt a quick start of the server using the same
        # port so we have to set the reuse flag.
        self.set_reuse_addr()
        try:
            self.bind(addr)
        except:
            # We really want to see these exceptions
            import traceback
            traceback.print_exc()
            raise
        self.listen(5)
        self.log('bound and listening')

    def log(self, msg, *args):
        log(self._label, msg, *args)

    def handle_accept(self):
        sock, addr = self.accept()
        self.log('in handle_accept()')
        # When we're done with everything, close the storage.  Do not write
        # the ack character until the storage is finished closing.
        if self._count <= 0:
            self.log('closing the storage')
            self._storage.close()
            if not self._keep:
                cleanup(self._storage)
            self.log('exiting')
            os._exit(0)
        self.log('continuing')
        sock.send('X')
        self._count -= 1


def main():
    label = 'zeoserver:%d' % os.getpid()
    log(label, 'starting')
    # We don't do much sanity checking of the arguments, since if we get it
    # wrong, it's a bug in the test suite.
    ro_svr = 0
    keep = 0
    configfile = None
    invalidation_queue_size = 100
    transaction_timeout = None
    # Parse the arguments and let getopt.error percolate
    opts, args = getopt.getopt(sys.argv[1:], 'rkC:Q:T:')
    for opt, arg in opts:
        if opt == '-r':
            ro_svr = 1
        elif opt == '-k':
            keep = 1
        elif opt == '-C':
            configfile = arg
        elif opt == '-Q':
            invalidation_queue_size = int(arg)
        elif opt == '-T':
            transaction_timeout = int(arg)
    # Open the config file and let ZConfig parse the data there.  Then remove
    # the config file, otherwise we'll leave turds.
    fp = open(configfile, 'r')
    storage = load_storage(fp)
    fp.close()
    os.remove(configfile)
    # The rest of the args are hostname, portnum
    zeo_port = int(args[0])
    test_port = zeo_port + 1
    try:
        log(label, 'creating the test server, ro: %s, keep: %s', ro_svr, keep)
        t = ZEOTestServer(('', test_port), storage, keep)
    except socket.error, e:
        if e[0] <> errno.EADDRINUSE: raise
        log(label, 'addr in use, closing and exiting')
        storage.close()
        cleanup(storage)
        sys.exit(2)
    addr = ('', zeo_port)
    log(label, 'creating the storage server')
    serv = ZEO.StorageServer.StorageServer(
        addr, {'1': storage}, ro_svr,
        invalidation_queue_size=invalidation_queue_size,
        transaction_timeout=transaction_timeout)
    log(label, 'entering ThreadedAsync loop')
    ThreadedAsync.LoopCallback.loop()


if __name__ == '__main__':
    main()
