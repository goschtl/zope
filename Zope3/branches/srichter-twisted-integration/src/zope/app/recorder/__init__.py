##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTTP session recorder.

$Id$
"""
__docformat__ = 'restructuredtext'

import time
import thread
import threading
import cStringIO

import twisted.web2.wsgi
from twisted.protocols import policies

import transaction
import ZODB.MappingStorage
from ZODB.POSException import ConflictError
from BTrees.IOBTree import IOBTree
from zope.app import wsgi
from zope.app.server.server import ServerType

class RecordingProtocol(policies.ProtocolWrapper):
    """A special protocol that keeps track of all input and output of an HTTP
    connection.

    The data is recorded for later analysis, such as generation of doc tests.  
    """

    def __init__(self, factory, wrappedProtocol):
        policies.ProtocolWrapper.__init__(self, factory, wrappedProtocol)
        self.input = cStringIO.StringIO()
        self.output = cStringIO.StringIO()
        self.chanRequest = None

    def dataReceived(self, data):
        self.input.write(data)
        policies.ProtocolWrapper.dataReceived(self, data)

    def write(self, data):
        if not self.chanRequest:
            self.chanRequest = self.wrappedProtocol.requests[-1]
        self.output.write(data)
        policies.ProtocolWrapper.write(self, data)

    def writeSequence(self, data):
        for entry in data:
            self.output.write(entry)
        policies.ProtocolWrapper.writeSequence(self, data)            

    def connectionLost(self, reason):
        policies.ProtocolWrapper.connectionLost(self, reason)

        if not self.chanRequest:
            return
        firstLine = self.output.getvalue().split('\r\n')[0]
        proto, status, reason = firstLine.split(' ', 2)
        requestStorage.add(RecordedRequest(
            time.time(),
            self.input.getvalue(),
            self.output.getvalue(),
            method = self.chanRequest.command.upper(),
            path = self.chanRequest.path,
            status = int(status),
            reason = reason
            ) )


class RecordingFactory(policies.WrappingFactory):
    """Special server factory that supports recording."""
    protocol = RecordingProtocol


def createRecordingHTTPFactory(db):
    resource = twisted.web2.wsgi.WSGIResource(
        wsgi.WSGIPublisherApplication(db))
    
    return RecordingFactory(twisted.web2.server.Site(resource))


class RecordedRequest(object):
    """A single recorded request and response."""

    def __init__(self, timestamp, request_string, response_string,
                 method=None, path=None, status=None, reason=None):
        self.timestamp = timestamp # float value, as returned by time.time()
        self.request_string = request_string
        self.response_string = response_string
        # The following attributes could be extracted from request_string and
        # response_string, but it is simpler to just take readily-available
        # values from RecordingProtocol.
        self.method = method
        self.path = path
        self.status = status
        self.reason = reason


class RequestStorage(object):
    """A collection of recorded requests.

    This class is thread-safe, that is, its methods can be called from multiple
    threads simultaneously.

    Most of thread safety comes from Python's global interpreter lock, but
    'add' needs extra locking.
    """

    def __init__(self):
        self._requests = {}
        self._lock = threading.Lock()

    def add(self, rr):
        """Add a RecordedRequest to the list."""
        self._lock.acquire()
        try:
            rr.id = len(self._requests) + 1
            self._requests[rr.id] = rr
        finally:
            self._lock.release()

    def __len__(self):
        """Return the number of recorded requests."""
        return len(self._requests)

    def __iter__(self):
        """List all recorded requests."""
        # Iterate over a new list object instead of calling itervalues, so that
        # we don't have to worry about other threads modifying the dict while
        # this thread is iterating over it.
        return iter(self._requests.values())

    def get(self, id):
        """Return the request with a given id, or None."""
        return self._requests.get(id)

    def clear(self):
        """Clear all recorded requests."""
        self._requests.clear()


#
# Globals
#

requestStorage = RequestStorage()

recordinghttp = ServerType(createRecordingHTTPFactory, 8081)
