##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bobo testing support

$Id$
"""

from StringIO import StringIO
import rfc822
import urllib

from zope.publisher.browser import TestRequest
from zope.publisher.publish import publish

from zope.bobo.publication import Publication

class Server:

    def __init__(self, resource_factory):
        self.publication = Publication(resource_factory)

    def request(self, request_string, handle_errors=True):
        """Execute an HTTP request string via the publisher

        This is used for HTTP doc tests.
        """

        # Discard leading white space to make call layout simpler
        request_string = request_string.lstrip()

        # split off and parse the command line
        l = request_string.find('\n')
        if l < 0:
            l = len(request_string)
        command_line = request_string[:l].rstrip()
        request_string = request_string[l+1:]
        method, path, protocol = command_line.split()
        path = urllib.unquote(path)

        instream = StringIO(request_string)
        environment = {"HTTP_HOST": 'localhost',
                       "HTTP_REFERER": 'localhost',
                       "REQUEST_METHOD": method,
                       "SERVER_PROTOCOL": protocol,
                       }

        headers = [split_header(header)
                   for header in rfc822.Message(instream).headers]
        for name, value in headers:
            name = ('_'.join(name.upper().split('-')))
            if name not in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
                name = 'HTTP_' + name
            environment[name] = value.rstrip()

        auth_key = 'HTTP_AUTHORIZATION'
        if environment.has_key(auth_key):
            environment[auth_key] = auth_header(environment[auth_key])

        outstream = StringIO()

        header_output = HTTPHeaderOutput(
            protocol, ('x-content-type-warning', 'x-powered-by'))

        request = self._request(path, environment, instream, outstream)
        request.response.setHeaderOutput(header_output)
        response = DocResponseWrapper(request.response, outstream,
                                      header_output)

        publish(request, handle_errors=handle_errors)

        return response
    
    def _request(self, path, environment, stdin, stdout):
        """Create a request
        """

        env = {}
        p=path.split('?')
        if len(p)==1:
            env['PATH_INFO'] = p[0]
        elif len(p)==2:
            env['PATH_INFO'], env['QUERY_STRING'] = p
        else:
            raise ValueError("Too many ?s in path", path)
        env.update(environment)

        request = TestRequest(stdin, stdout, env)
        request.setPublication(self.publication)

        return request



class HTTPHeaderOutput:

    def __init__(self, protocol, omit):
        self.headers = {}
        self.headersl = []
        self.protocol = protocol
        self.omit = omit
    
    def setResponseStatus(self, status, reason):
        self.status, self.reason = status, reason

    def setResponseHeaders(self, mapping):
        self.headers.update(dict(
            [('-'.join([s.capitalize() for s in name.split('-')]), v)
             for name, v in mapping.items()
             if name.lower() not in self.omit]
        ))

    def appendResponseHeaders(self, lst):
        headers = [split_header(header) for header in lst]
        self.headersl.extend(
            [('-'.join([s.capitalize() for s in name.split('-')]), v)
             for name, v in headers
             if name.lower() not in self.omit]
        )

    def __str__(self):
        out = ["%s: %s" % header for header in self.headers.items()]
        out.extend(["%s: %s" % header for header in self.headersl])
        out.sort()
        out.insert(0, "%s %s %s" % (self.protocol, self.status, self.reason))
        return '\n'.join(out)

class DocResponseWrapper:
    """Response Wrapper for use in doc tests
    """

    def __init__(self, response, outstream, header_output):
        self._response = response
        self._outstream = outstream
        self.header_output = header_output

    def getBody(self):
        """Returns the full HTTP output (headers + body)"""
        return self._outstream.getvalue()

    def __str__(self):
        body = self.getBody()
        if body:
            return "%s\n\n%s" % (self.header_output, body)
        return "%s\n" % (self.header_output)

    def __getattr__(self, attr):
        return getattr(self._response, attr)
