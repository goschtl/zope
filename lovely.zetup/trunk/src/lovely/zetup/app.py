##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = 'restructuredtext'

import xmlrpclib

from zope import interface

import zope.publisher.xmlrpc
from zope.app.wsgi import WSGIPublisherApplication
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.publisher.browser import BrowserRequest
from zope.app.publication.httpfactory import chooseClasses
from publication import NoZODBPublication
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.browser import setDefaultSkin
from zope.publisher.publish import publish


class XMLRPCRequest(zope.publisher.xmlrpc.XMLRPCRequest):

    def processInputs(self):
        'See IPublisherRequest'
        # override because we only read content_length in locking sockets
        length = int(self._environ.get('CONTENT_LENGTH'))
        lines = self._body_instream.read(length)
        self._args, function = xmlrpclib.loads(lines)
        # Translate '.' to '/' in function to represent object
        # traversal.
        function = function.split('.')
        if function:
            self.setPathSuffix(function)


class PublicationRequestFactory(object):
    interface.implements(IPublicationRequestFactory)

    def __init__(self):

        """See `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        self._publication_cache = {}
        self._publication = NoZODBPublication()

    def __call__(self, input_stream, env):

        """See
        `zope.app.publication.interfaces.IPublicationRequestFactory`"""
        method = env.get('REQUEST_METHOD', 'GET').upper()
        requestClass, publicationClass = chooseClasses(method, env)
        request = requestClass(input_stream, env)
        # we must hack the publication's getApplication method because it uses
        # ZODB.
        publication = publicationClass(None)
        publication.getApplication = self._publication.getApplication
        publication._app = self._publication._app
        request.setPublication(publication)
        if IBrowserRequest.providedBy(request):
            # only browser requests have skins
            setDefaultSkin(request)
        return request

class Application(WSGIPublisherApplication):

    def __init__(self):
        self.requestFactory = PublicationRequestFactory()

    def __call__(self, environ, start_response):
        """See zope.app.wsgi.interfaces.IWSGIApplication"""
        request = self.requestFactory(environ['wsgi.input'], environ)
        # Let's support post-mortem debugging
        if 'HTTP_X_ZOPE_HANDLE_ERRORS' in environ:
            handle_errors = environ.get('HTTP_X_ZOPE_HANDLE_ERRORS') == 'True'
        else:
            handle_errors = environ.get('wsgi.handleErrors', True)
        request = publish(request, handle_errors=handle_errors)
        response = request.response

        # Start the WSGI server response
        start_response(response.getStatusString(), response.getHeaders())

        # Return the result body iterable.
        return response.consumeBodyIter()

