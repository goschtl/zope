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
import asyncore
import os
import random
import select
import socket
import sys
import tempfile
import thread
import time

import zLOG

import ZEO.ClientStorage
from ZEO.Exceptions import Disconnected

from ZODB.Transaction import get_transaction
from ZODB.POSException import ReadOnlyError
from ZODB.tests import StorageTestBase
from ZODB.tests.StorageTestBase import zodb_unpickle, MinPO

class ConnectionTests(StorageTestBase.StorageTestBase):
    """Tests that explicitly manage the server process.

    To test the cache or re-connection, these test cases explicit
    start and stop a ZEO storage server.
    """

    __super_tearDown = StorageTestBase.StorageTestBase.tearDown

    def setUp(self):
        """Start a ZEO server using a Unix domain socket

        The ZEO server uses the storage object returned by the
        getStorage() method.
        """
        zLOG.LOG("testZEO", zLOG.INFO, "setUp() %s" % self.id())
        self.file = tempfile.mktemp()
        self.addr = []
        self._pids = []
        self._servers = []
        self._newAddr()
        self.startServer()

    # startServer(), shutdownServer() are defined in OS-specific subclasses

    def _newAddr(self):
        self.addr.append(self._getAddr())

    def _getAddr(self):
        # On windows, port+1 is also used (see winserver.py), so only
        # draw even port numbers
        return 'localhost', random.randrange(25000, 30000, 2)

    def openClientStorage(self, cache='', cache_size=200000, wait=1,
                          read_only=0, read_only_fallback=0):
        raise NotImplementedError

    def shutdownServer(self, index=0):
        raise NotImplementedError

    def startServer(self, create=1, index=0, read_only=0, ro_svr=0):
        raise NotImplementedError

    def tearDown(self):
        """Try to cause the tests to halt"""
        zLOG.LOG("testZEO", zLOG.INFO, "tearDown() %s" % self.id())
        if getattr(self, '_storage', None) is not None:
            self._storage.close()
        for i in range(len(self._servers)):
            self.shutdownServer(i)
        # file storage appears to create four files
        for i in range(len(self.addr)):
            for ext in '', '.index', '.lock', '.tmp':
                path = "%s.%s%s" % (self.file, i, ext)
                if os.path.exists(path):
                    try:
                        os.unlink(path)
                    except os.error:
                        pass
        for i in 0, 1:
            path = "c1-test-%d.zec" % i
            if os.path.exists(path):
                try:
                    os.unlink(path)
                except os.error:
                    pass
        self.__super_tearDown()

    def pollUp(self, timeout=30.0):
        # Poll until we're connected
        now = time.time()
        giveup = now + timeout
        while not self._storage.is_connected():
            asyncore.poll(0.1)
            now = time.time()
            if now > giveup:
                self.fail("timed out waiting for storage to connect")

    def pollDown(self, timeout=30.0):
        # Poll until we're disconnected
        now = time.time()
        giveup = now + timeout
        while self._storage.is_connected():
            asyncore.poll(0.1)
            now = time.time()
            if now > giveup:
                self.fail("timed out waiting for storage to disconnect")

    def checkMultipleAddresses(self):
        for i in range(4):
            self._newAddr()
        self._storage = self.openClientStorage('test', 100000, wait=1)
        oid = self._storage.new_oid()
        obj = MinPO(12)
        self._dostore(oid, data=obj)
        self._storage.close()

    def checkMultipleServers(self):
        # XXX crude test at first -- just start two servers and do a
        # commit at each one.

        self._newAddr()
        self._storage = self.openClientStorage('test', 100000, wait=1)
        self._dostore()

        self.shutdownServer(index=0)
        self.startServer(index=1)

        # If we can still store after shutting down one of the
        # servers, we must be reconnecting to the other server.

        for i in range(10):
            try:
                self._dostore()
                break
            except Disconnected:
                time.sleep(0.5)

    def checkReadOnlyClient(self):
        # Open a read-only client to a read-write server; stores fail

        # Start a read-only client for a read-write server
        self._storage = self.openClientStorage(read_only=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

    def checkReadOnlyStorage(self):
        # Open a read-only client to a read-only *storage*; stores fail

        # We don't want the read-write server created by setUp()
        self.shutdownServer()
        self._servers = []
        self._pids = []

        # Start a read-only server
        self.startServer(create=0, index=0, read_only=1)
        # Start a read-only client
        self._storage = self.openClientStorage(read_only=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

    def checkReadOnlyServer(self):
        # Open a read-only client to a read-only *server*; stores fail

        # We don't want the read-write server created by setUp()
        self.shutdownServer()
        self._servers = []
        self._pids = []

        # Start a read-only server
        self.startServer(create=0, index=0, ro_svr=1)
        # Start a read-only client
        self._storage = self.openClientStorage(read_only=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

    def checkReadOnlyFallbackWritable(self):
        # Open a fallback client to a read-write server; stores succeed

        # Start a read-only-fallback client for a read-write server
        self._storage = self.openClientStorage(read_only_fallback=1)
        # Stores should succeed here
        self._dostore()

    def checkReadOnlyFallbackReadOnlyStorage(self):
        # Open a fallback client to a read-only *storage*; stores fail

        # We don't want the read-write server created by setUp()
        self.shutdownServer()
        self._servers = []
        self._pids = []

        # Start a read-only server
        self.startServer(create=0, index=0, read_only=1)
        # Start a read-only-fallback client
        self._storage = self.openClientStorage(wait=1, read_only_fallback=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

    def checkReadOnlyFallbackReadOnlyServer(self):
        # Open a fallback client to a read-only *server*; stores fail

        # We don't want the read-write server created by setUp()
        self.shutdownServer()
        self._servers = []
        self._pids = []

        # Start a read-only server
        self.startServer(create=0, index=0, ro_svr=1)
        # Start a read-only-fallback client
        self._storage = self.openClientStorage(wait=1, read_only_fallback=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

    # XXX Compare checkReconnectXXX() here to checkReconnection()
    # further down.  Is the code here hopelessly naive, or is
    # checkReconnection() overwrought?

    def checkReconnectWritable(self):
        # A read-write client reconnects to a read-write server

        # Start a client
        self._storage = self.openClientStorage(wait=1)
        # Stores should succeed here
        self._dostore()

        # Shut down the server
        self.shutdownServer()
        self._servers = []
        self._pids = []
        # Poll until the client disconnects
        self.pollDown()
        # Stores should fail now
        self.assertRaises(Disconnected, self._dostore)

        # Restart the server
        self.startServer(create=0)
        # Poll until the client connects
        self.pollUp()
        # Stores should succeed here
        self._dostore()

    def checkReconnectReadOnly(self):
        # A read-only client reconnects from a read-write to a
        # read-only server

        # Start a client
        self._storage = self.openClientStorage(wait=1, read_only=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

        # Shut down the server
        self.shutdownServer()
        self._servers = []
        self._pids = []
        # Poll until the client disconnects
        self.pollDown()
        # Stores should still fail
        self.assertRaises(ReadOnlyError, self._dostore)

        # Restart the server
        self.startServer(create=0, read_only=1)
        # Poll until the client connects
        self.pollUp()
        # Stores should still fail
        self.assertRaises(ReadOnlyError, self._dostore)

    def checkReconnectFallback(self):
        # A fallback client reconnects from a read-write to a
        # read-only server

        # Start a client in fallback mode
        self._storage = self.openClientStorage(wait=1, read_only_fallback=1)
        # Stores should succeed here
        self._dostore()

        # Shut down the server
        self.shutdownServer()
        self._servers = []
        self._pids = []
        # Poll until the client disconnects
        self.pollDown()
        # Stores should fail now
        self.assertRaises(Disconnected, self._dostore)

        # Restart the server
        self.startServer(create=0, read_only=1)
        # Poll until the client connects
        self.pollUp()
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

    def checkReconnectUpgrade(self):
        # A fallback client reconnects from a read-only to a
        # read-write server

        # We don't want the read-write server created by setUp()
        self.shutdownServer()
        self._servers = []
        self._pids = []

        # Start a read-only server
        self.startServer(create=0, read_only=1)
        # Start a client in fallback mode
        self._storage = self.openClientStorage(wait=1, read_only_fallback=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

        # Shut down the server
        self.shutdownServer()
        self._servers = []
        self._pids = []
        # Poll until the client disconnects
        self.pollDown()
        # Stores should fail now
        self.assertRaises(Disconnected, self._dostore)

        # Restart the server, this time read-write
        self.startServer(create=0)
        # Poll until the client sconnects
        self.pollUp()
        # Stores should now succeed
        self._dostore()

    def checkReconnectSwitch(self):
        # A fallback client initially connects to a read-only server,
        # then discovers a read-write server and switches to that

        # We don't want the read-write server created by setUp()
        self.shutdownServer()
        self._servers = []
        self._pids = []

        # Allocate a second address (for the second server)
        self._newAddr()

        # Start a read-only server
        self.startServer(create=0, index=0, read_only=1)
        # Start a client in fallback mode
        self._storage = self.openClientStorage(wait=1, read_only_fallback=1)
        # Stores should fail here
        self.assertRaises(ReadOnlyError, self._dostore)

        # Start a read-write server
        self.startServer(index=1, read_only=0)
        # After a while, stores should work
        for i in range(300): # Try for 30 seconds
            try:
                self._dostore()
                break
            except (Disconnected, ReadOnlyError,
                    select.error, thread.error, socket.error):
                time.sleep(0.1)
        else:
            self.fail("Couldn't store after starting a read-write server")

    def checkDisconnectionError(self):
        # Make sure we get a Disconnected when we try to read an
        # object when we're not connected to a storage server and the
        # object is not in the cache.
        self.shutdownServer()
        self._storage = self.openClientStorage('test', 1000, wait=0)
        self.assertRaises(Disconnected, self._storage.load, 'fredwash', '')

    def checkBasicPersistence(self):
        # Verify cached data persists across client storage instances.

        # To verify that the cache is being used, the test closes the
        # server and then starts a new client with the server down.
        # When the server is down, a load() gets the data from its cache.

        self._storage = self.openClientStorage('test', 100000, wait=1)
        oid = self._storage.new_oid()
        obj = MinPO(12)
        revid1 = self._dostore(oid, data=obj)
        self._storage.close()
        self.shutdownServer()
        self._storage = self.openClientStorage('test', 100000, wait=0)
        data, revid2 = self._storage.load(oid, '')
        self.assertEqual(zodb_unpickle(data), MinPO(12))
        self.assertEqual(revid1, revid2)
        self._storage.close()

    def checkRollover(self):
        # Check that the cache works when the files are swapped.

        # In this case, only one object fits in a cache file.  When the
        # cache files swap, the first object is effectively uncached.

        self._storage = self.openClientStorage('test', 1000, wait=1)
        oid1 = self._storage.new_oid()
        obj1 = MinPO("1" * 500)
        self._dostore(oid1, data=obj1)
        oid2 = self._storage.new_oid()
        obj2 = MinPO("2" * 500)
        self._dostore(oid2, data=obj2)
        self._storage.close()
        self.shutdownServer()
        self._storage = self.openClientStorage('test', 1000, wait=0)
        self._storage.load(oid1, '')
        self._storage.load(oid2, '')

    def checkReconnection(self):
        # Check that the client reconnects when a server restarts.

        # XXX Seem to get occasional errors that look like this:
        # File ZEO/zrpc2.py, line 217, in handle_request
        # File ZEO/StorageServer.py, line 325, in storea
        # File ZEO/StorageServer.py, line 209, in _check_tid
        # StorageTransactionError: (None, <tid>)
        # could system reconnect and continue old transaction?

        self._storage = self.openClientStorage()
        oid = self._storage.new_oid()
        obj = MinPO(12)
        self._dostore(oid, data=obj)
        zLOG.LOG("checkReconnection", zLOG.INFO,
                 "About to shutdown server")
        self.shutdownServer()
        zLOG.LOG("checkReconnection", zLOG.INFO,
                 "About to restart server")
        self.startServer(create=0)
        oid = self._storage.new_oid()
        obj = MinPO(12)
        while 1:
            try:
                self._dostore(oid, data=obj)
                break
            except (Disconnected, select.error, thread.error, socket.error):
                zLOG.LOG("checkReconnection", zLOG.INFO,
                         "Error after server restart; retrying.",
                         error=sys.exc_info())
                get_transaction().abort()
                time.sleep(0.1) # XXX how long to sleep
            # XXX This is a bloody pain.  We're placing a heavy burden
            # on users to catch a plethora of exceptions in order to
            # write robust code.  Need to think about implementing
            # John Heintz's suggestion to make sure all exceptions
            # inherit from POSException.
        zLOG.LOG("checkReconnection", zLOG.INFO, "finished")

