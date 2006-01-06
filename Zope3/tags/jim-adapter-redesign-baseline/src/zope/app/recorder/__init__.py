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
"""
HTTP session recorder.

$Id$
"""
__docformat__ = 'restructuredtext'

import thread
import threading
import transaction
import ZODB.MappingStorage
from ZODB.POSException import ConflictError
from BTrees.IOBTree import IOBTree
from zope.app.publication.httpfactory import HTTPPublicationRequestFactory
from zope.app.server.servertype import ServerType
from zope.server.http.commonaccesslogger import CommonAccessLogger
from zope.server.http.publisherhttpserver import PublisherHTTPServer
from zope.server.http.httpserverchannel import HTTPServerChannel
from zope.server.http.httprequestparser import HTTPRequestParser
from zope.server.http.httptask import HTTPTask
from zope.publisher.publish import publish


class RecordingHTTPTask(HTTPTask):
    """An HTTPTask that remembers the response as a string."""

    def __init__(self, *args, **kw):
        self._response_data = []
        HTTPTask.__init__(self, *args, **kw)

    def write(self, data):
        """Send data to the client.

        Wraps HTTPTask.write and records the response.
        """
        if not self.wrote_header:
            # HTTPTask.write will call self.buildResponseHeader() and send the
            # result before sending 'data'.  This code assumes that
            # buildResponseHeader will return the same string when called the
            # second time.
            self._response_data.append(self.buildResponseHeader())
        HTTPTask.write(self, data)
        self._response_data.append(data)

    def getRawResponse(self):
        """Return the full HTTP response as a string."""
        return ''.join(self._response_data)


class RecordingHTTPRequestParser(HTTPRequestParser):
    """An HTTPRequestParser that remembers the raw request as a string."""

    def __init__(self, *args, **kw):
        self._request_data = []
        HTTPRequestParser.__init__(self, *args, **kw)

    def received(self, data):
        """Process data received from the client.

        Wraps HTTPRequestParser.write and records the request.
        """
        consumed = HTTPRequestParser.received(self, data)
        self._request_data.append(data[:consumed])
        return consumed

    def getRawRequest(self):
        """Return the full HTTP request as a string."""
        return ''.join(self._request_data)


class RecordingHTTPServerChannel(HTTPServerChannel):
    """An HTTPServerChannel that records request and response."""

    task_class = RecordingHTTPTask
    parser_class = RecordingHTTPRequestParser


class RecordingHTTPServer(PublisherHTTPServer):
    """Zope Publisher-specific HTTP server that can record requests."""

    channel_class = RecordingHTTPServerChannel
    num_retries = 10

    def executeRequest(self, task):
        """Process a request.

        Wraps PublisherHTTPServer.executeRequest().
        """
        PublisherHTTPServer.executeRequest(self, task)
        # PublisherHTTPServer either committed or aborted a transaction,
        # so we need a new one.
        # TODO: Actually, we only need a transaction if we use
        #       ZODBBasedRequestStorage, which we don't since it has problems
        #       keeping data fresh enough.  This loop will go away soon, unless
        #       I manage to fix ZODBBasedRequestStorage.
        for n in range(self.num_retries):
            try:
                txn = transaction.begin()
                txn.note("request recorder")
                requestStorage.add(RecordedRequest.fromHTTPTask(task))
                transaction.commit()
            except ConflictError:
                transaction.abort()
                if n == self.num_retries - 1:
                    raise
            else:
                break


class RecordedRequest(object):
    """A single recorded request and response."""

    def __init__(self, timestamp, request_string, response_string,
                 method=None, path=None, status=None, reason=None):
        self.timestamp = timestamp # float value, as returned by time.time()
        self.request_string = request_string
        self.response_string = response_string
        # The following attributes could be extracted from request_string and
        # response_string, but it is simpler to just take readily-available
        # values from RecordingHTTPTask.
        self.method = method
        self.path = path
        self.status = status
        self.reason = reason

    def fromHTTPTask(cls, task):
        """Create a RecordedRequest with data extracted from RecordingHTTPTask.
        """
        rq = cls(timestamp=task.start_time,
                 request_string=task.request_data.getRawRequest(),
                 response_string=task.getRawResponse(),
                 method=task.request_data.command.upper(),
                 path=task.request_data.path,
                 status=task.status,
                 reason=task.reason)
        return rq

    fromHTTPTask = classmethod(fromHTTPTask)


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


class ZODBBasedRequestStorage(object):
    """A collection of recorded requests.

    This class is thread-safe, that is, its methods can be called from multiple
    threads simultaneously.

    In addition, it is transactional.

    TODO: The simple ID allocation strategy used by RequestStorage.add will
          cause frequent conflict errors.  Something should be done about that.

    TODO: _getData() tends to return stale data, and you need to refresh the
          ++etc++process/RecordedSessions.html page two or three times until
          it becomes up to date.

    TODO: This class is not used because of the previous problem.  Either fix
          the problem, or remove this class.
    """

    _key = 'RequestStorage'

    def __init__(self):
        self._ram_storage = ZODB.MappingStorage.MappingStorage()
        self._ram_db = ZODB.DB(self._ram_storage)
        self._conns = {}

    def _getData(self):
        """Get the shared data container from the mapping storage."""
        # This method closely mimics RAMSessionDataContainer._getData
        # from zope.app.session.session
        tid = thread.get_ident()
        if tid not in self._conns:
            self._conns[tid] = self._ram_db.open()
        root = self._conns[tid].root()
        if self._key not in root:
            root[self._key] = IOBTree()
        return root[self._key]

    def add(self, rr):
        """Add a RecordedRequest to the list."""
        requests = self._getData()
        rr.id = len(requests) + 1
        requests[rr.id] = rr

    def __len__(self):
        """Return the number of recorded requests."""
        return len(self._getData())

    def __iter__(self):
        """List all recorded requests."""
        return iter(self._getData().values())

    def get(self, id):
        """Return the request with a given id, or None."""
        requests = self._getData()
        return requests.get(id)

    def clear(self):
        """Clear all recorded requests."""
        self._getData().clear()


#
# Globals
#

requestStorage = RequestStorage()

recordinghttp = ServerType(RecordingHTTPServer,
                           HTTPPublicationRequestFactory,
                           CommonAccessLogger,
                           8081, True)
