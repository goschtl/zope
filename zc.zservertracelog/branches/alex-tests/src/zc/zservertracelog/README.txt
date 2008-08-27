==================
 ZServer TraceLog
==================

A tracelog is a kind of access log that records several low-level events for
each request.  Each log entry starts with a record type, a request identifier
and the time.  Some log records have additional data.

    >>> import zc.zservertracelog.tracelog
    >>> import zope.app.appsetup.interfaces

For these examples, we'll add a log handler that outputs to standard out.

    >>> import logging
    >>> import sys
    >>> stdout_handler = logging.StreamHandler(sys.stdout)

    >>> logger = logging.getLogger('zc.tracelog')
    >>> logger.setLevel(logging.INFO)
    >>> logger.addHandler(stdout_handler)

There is an event handler to log when the Z server starts.

    >>> zc.zservertracelog.tracelog.started(
    ...     zope.app.appsetup.interfaces.ProcessStarting())
    S 0 2008-08-26T11:55:00

The tracelog machinery is implemented as a WSGI layer, so we'll define a fake
WSGI application for tracelog to use.

    >>> def faux_application(environ, start_response):
    ...     """Fake WSGI application.  Doesn't need to do much!"""

Now, let's create an instance of the tracelog server.

    >>> addr, port = '127.0.0.1', 12345

    >>> trace_server = zc.zservertracelog.tracelog.Server(
    ...     faux_application, None, addr, port)

Let's also define a convenience function for processing requests.

    >>> def invokeRequest(req):
    ...     channel = trace_server.channel_class(trace_server, None, addr)
    ...     channel.received(req)

Process a simple request.

    >>> req1 = """\
    ... GET / HTTP/1.1
    ... Host: www.example.com
    ...
    ... """

    >>> invokeRequest(req1)
    B 23423600 2008-08-27T10:54:08 GET /
    I 23423600 2008-08-27T10:54:08 0
    C 23423600 2008-08-27T10:54:08
    A 23423600 2008-08-27T10:54:08 200 ?
    E 23423600 2008-08-27T10:54:08
