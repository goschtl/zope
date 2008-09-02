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


Server Startup
==============

There is an event handler to log when the Z server starts.

    >>> zc.zservertracelog.tracelog.started(
    ...     zope.app.appsetup.interfaces.ProcessStarting())
    S 0 2008-08-26T11:55:00


Tracing Applications
====================

The tracelog machinery is implemented as a WSGI layer, so we'll pass a fake
WSGI application to tracelog for these examples.

    >>> faux_app = FauxApplication()

Now, let's create an instance of the tracelog server.

    >>> addr, port = '127.0.0.1', 12345

    >>> trace_server = zc.zservertracelog.tracelog.Server(
    ...     faux_app, None, addr, port)

Let's also define a convenience function for processing requests.

    >>> def invokeRequest(req):
    ...     channel = trace_server.channel_class(trace_server, None, addr)
    ...     channel.received(req)

Process a simple request.

    >>> req1 = """\
    ... GET /test-req1 HTTP/1.1
    ... Host: www.example.com
    ...
    ... """

    >>> invokeRequest(req1)
    B 23423600 2008-08-27T10:54:08 GET /test-req1
    I 23423600 2008-08-27T10:54:08 0
    C 23423600 2008-08-27T10:54:08
    A 23423600 2008-08-27T10:54:08 200 ?
    E 23423600 2008-08-27T10:54:08


Application Errors
==================

The tracelog will also log application errors.  To show this, we'll set up
our test application to raise an error when called.

    >>> def test_failure(*args, **kwargs):
    ...     raise Exception('oh noes!')
    >>> faux_app.app_hook = test_failure

We can see that all trace points were hit and that the error was written to
the log.

    >>> try:
    ...     invokeRequest(req1)
    ... except:
    ...     pass
    B 21663984 2008-09-02T11:19:26 GET /test-req1
    I 21663984 2008-09-02T11:19:26 0
    C 21663984 2008-09-02T11:19:26
    A 21663984 2008-09-02T11:19:26 Error: oh noes!
    E 21663984 2008-09-02T11:19:26


TODO
====

  * show a task write exception
