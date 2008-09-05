##############################################################################
#
# Copyright (c) 2005, 2008 Zope Corporation and Contributors.
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
"""Crude Tracelog Hack for ZServer
"""
from zope.app.server import servertype
from zope.app.wsgi import WSGIPublisherApplication
from zope.server.http import wsgihttpserver
from zope.server.http.commonaccesslogger import CommonAccessLogger
import datetime
import logging
import re
import zc.zservertracelog.interfaces
import zope.app.appsetup.interfaces
import zope.component
import zope.server.http.httprequestparser
import zope.server.http.httpserverchannel


tracelog = logging.getLogger('zc.tracelog')


def _format_datetime(dt):
    return dt.replace(microsecond=0).isoformat()


def _run_trace_extensions(trace_point, logger):
    tracers = zope.component.getUtilitiesFor(trace_point)
    for tname, tracer in tracers:
        tracer(logger, trace_point)


class TraceLog(object):
    zope.interface.implements(zc.zservertracelog.interfaces.ITraceLog)

    def __init__(self, channel):
        self.channel_id = id(channel)

    # this implementation adds a `trace_code` option which is meant to be
    # used internally and not for use by extensions.
    def log(
        self, msg=None, timestamp=None, extension_id=None, trace_code=None):

        if timestamp is None:
            timestamp = datetime.datetime.now()

        if not trace_code:
            trace_code = 'X'

        if trace_code == 'X' and extension_id is None:
            raise ValueError('extension_id is required')

        entry = '%s %s %s' % (
            trace_code, self.channel_id, _format_datetime(timestamp))

        if extension_id:
            entry += ' %s' % extension_id

        if msg:
            entry += ' %s' % msg

        tracelog.info(entry)


class Parser(zope.server.http.httprequestparser.HTTPRequestParser):

    def __init__(self, x):
        self._Channel__B = datetime.datetime.now()
        zope.server.http.httprequestparser.HTTPRequestParser.__init__(self, x)


class Channel(zope.server.http.httpserverchannel.HTTPServerChannel):
    parser_class = Parser

    def handle_request(self, parser):
        logger = TraceLog(self)
        logger.log(
            '%s %s' % (parser.command, parser.path),
            parser.__B,
            trace_code='B')
        _run_trace_extensions(
            zc.zservertracelog.interfaces.ITraceRequestStart, logger)
        logger.log(str(parser.content_length), trace_code='I')
        _run_trace_extensions(
            zc.zservertracelog.interfaces.ITraceRequestInputAcquired, logger)
        zope.server.http.httpserverchannel.HTTPServerChannel.handle_request(
            self, parser)


status_match = re.compile('(\d+) (.*)').match
class Server(wsgihttpserver.WSGIHTTPServer):

    channel_class = Channel

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

    def executeRequest(self, task):
        """Overrides HTTPServer.executeRequest()."""
        logger = TraceLog(task.channel)
        logger.log(trace_code='C')
        _run_trace_extensions(
            zc.zservertracelog.interfaces.ITraceApplicationStart, logger)
        env = task.getCGIEnvironment()
        env['wsgi.input'] = task.request_data.getBodyStream()

        def start_response(status, headers):
            # Prepare the headers for output
            status, reason = status_match(status).groups()
            task.setResponseStatus(status, reason)
            task.appendResponseHeaders(['%s: %s' % i for i in headers])

            # Return the write method used to write the response data.
            return wsgihttpserver.fakeWrite

        # Call the application to handle the request and write a response
        try:
            response = self.application(env, start_response)
        except Exception, v:
            logger.log('Error: %s' % v, trace_code='A')
            _run_trace_extensions(
                zc.zservertracelog.interfaces.ITraceApplicationEnd, logger)
            logger.log(trace_code='E')
            _run_trace_extensions(
                zc.zservertracelog.interfaces.ITraceRequestEnd, logger)
            raise
        else:
            accumulated_headers = getattr(task, 'accumulated_headers') or ()
            length = [h.split(': ')[1].strip()
                      for h in accumulated_headers
                      if h.lower().startswith('content-length: ')]
            if length:
                length = length[0]
            else:
                length = '?'

            logger.log(
                '%s %s' % (getattr(task, 'status', '?'), length),
                trace_code='A')
            _run_trace_extensions(
                zc.zservertracelog.interfaces.ITraceApplicationEnd, logger)

            try:
                task.write(response)
            except Exception, v:
                logger.log('Error: %s' % v, trace_code='E')
                _run_trace_extensions(
                    zc.zservertracelog.interfaces.ITraceRequestEnd, logger)
                raise
            else:
                logger.log(trace_code='E')
                _run_trace_extensions(
                    zc.zservertracelog.interfaces.ITraceRequestEnd, logger)


http = servertype.ServerType(
    Server,
    WSGIPublisherApplication,
    CommonAccessLogger,
    8080, True)


pmhttp = servertype.ServerType(
    wsgihttpserver.PMDBWSGIHTTPServer,
    WSGIPublisherApplication,
    CommonAccessLogger,
    8013, True)


@zope.component.adapter(zope.app.appsetup.interfaces.IProcessStartingEvent)
def started(event):
    tracelog.info('S 0 %s', _format_datetime(datetime.datetime.now()))
