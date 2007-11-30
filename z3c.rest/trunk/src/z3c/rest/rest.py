##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""REST publication and publisher factories

$Id$
"""
import cgi
import zope.interface
from zope.app.publication.interfaces import IPublicationRequestFactory
from zope.app.publication.http import HTTPPublication
from zope.publisher.http import HTTPRequest

from z3c.rest import interfaces

class RESTRequest(HTTPRequest):
    zope.interface.implements(interfaces.IRESTRequest)

    __slots__ = (
        'parameters', # Parameters sent via the query string.
        )

    def __init__(self, body_instream, environ, response=None):
        self.parameters = {}
        super(RESTRequest, self).__init__(body_instream, environ, response)

    def processInputs(self):
        'See IPublisherRequest'
        if 'QUERY_STRING' not in self._environ:
            return
        # Parse the query string into our parameters dictionary.
        self.parameters = cgi.parse_qs(
            self._environ['QUERY_STRING'], keep_blank_values=1)
        # Since the parameter value is always a list (sigh), let's at least
        # detect single values and store them.
        for name, value in self.parameters.items():
            if len(value) == 1:
                self.parameters[name] = value[0]

    def keys(self):
        'See Interface.Common.Mapping.IEnumerableMapping'
        d = {}
        d.update(self._environ)
        d.update(self.parameters)
        return d.keys()

    def get(self, key, default=None):
        'See Interface.Common.Mapping.IReadMapping'
        marker = object()
        result = self.parameters.get(key, marker)
        if result is not marker:
            return result

        return super(RESTRequest, self).get(key, default)


class RESTView(object):
    zope.interface.implements(interfaces.IRESTView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @apply
    def __parent__():
        def get(self):
            return getattr(self, '_parent', self.context)
        def set(self, parent):
            self._parent = parent
        return property(get, set)


class RESTPublicationRequestFactory(object):
    zope.interface.implements(IPublicationRequestFactory)

    def __init__(self, db):
        """See zope.app.publication.interfaces.IPublicationRequestFactory"""
        self.publication = HTTPPublication(db)

    def __call__(self, input_stream, env, output_stream=None):
        """See zope.app.publication.interfaces.IPublicationRequestFactory"""
        request = RESTRequest(input_stream, env)
        request.setPublication(self.publication)
        return request
