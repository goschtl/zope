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


def _log(channel_id, trace_code='-', msg=None, timestamp=None):
    if timestamp is None:
        timestamp = datetime.datetime.now()

    entry = '%s %s %s' % (trace_code, channel_id, _format_datetime(timestamp))

    if msg:
        entry += ' %s' % repr(msg)[1:-1]

    tracelog.info(entry)


@zope.component.adapter(zope.publisher.interfaces.IRequest)
@zope.interface.implementer(zc.zservertracelog.interfaces.ITraceLog)
def get(request):
    return request['zc.zservertracelog.interfaces.ITraceLog']


class TraceLog(object):
    zope.interface.implements(zc.zservertracelog.interfaces.ITraceLog)

    def __init__(self, channel_id):
        self.channel_id = channel_id

    def log(self, msg=None):
        _log(self.channel_id, '-', msg)


class Parser(zope.server.http.httprequestparser.HTTPRequestParser):

    def __init__(self, x):
        self._Channel__B = datetime.datetime.now()
        zope.server.http.httprequestparser.HTTPRequestParser.__init__(self, x)


class Channel(zope.server.http.httpserverchannel.HTTPServerChannel):
    parser_class = Parser

    def handle_request(self, parser):
        full_path = parser.path
        if parser.query:
            full_path += '?%s' % parser.query
        elif parser.query is not None:
            full_path += '?'

        cid = id(self)
        _log(cid, 'B', '%s %s' % (parser.command, full_path), parser.__B)
        _log(cid, 'I', str(parser.content_length))

        zope.server.http.httpserverchannel.HTTPServerChannel.handle_request(
            self, parser)


status_match = re.compile('(\d+) (.*)').match
class Server(wsgihttpserver.WSGIHTTPServer):

    channel_class = Channel

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)

    def executeRequest(self, task):
        """Overrides HTTPServer.executeRequest()."""
        cid = id(task.channel)
        _log(cid, 'C')
        env = task.getCGIEnvironment()
        env['wsgi.input'] = task.request_data.getBodyStream()
        env['zc.zservertracelog.interfaces.ITraceLog'] = TraceLog(cid)

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
            _log(cid, 'A', 'Error: %s' % v)
            _log(cid, 'E')
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

            _log(cid, 'A', '%s %s' % (getattr(task, 'status', '?'), length))

            try:
                task.write(response)
            except Exception, v:
                _log(cid, 'E', 'Error: %s' % v)
                raise
            else:
                _log(cid, 'E')


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
