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
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""HTTP Factory

$Id: httpfactory.py,v 1.7 2004/03/20 13:37:02 philikon Exp $
"""
from zope.interface import moduleProvides, implements
from zope.publisher.http import HTTPRequest
from zope.publisher.browser import BrowserRequest
from zope.publisher.xmlrpc import XMLRPCRequest

from zope.app.process.interfaces import IPublicationRequestFactoryFactory
from zope.app.process.interfaces import IPublicationRequestFactory

from zope.app.publication.http import HTTPPublication
from zope.app.publication.browser import BrowserPublication
from zope.app.publication.xmlrpc import XMLRPCPublication

moduleProvides(IPublicationRequestFactoryFactory)

__metaclass__ = type

_browser_methods = 'GET', 'POST', 'HEAD'

class HTTPPublicationRequestFactory:
    implements(IPublicationRequestFactory)

    def __init__(self, db):
        """See zope.app.process.interfaces.IPublicationRequestFactory"""
        self._http = HTTPPublication(db)
        self._brower = BrowserPublication(db)
        self._xmlrpc = XMLRPCPublication(db)

    def __call__(self, input_stream, output_steam, env):
        """See zope.app.process.interfaces.IPublicationRequestFactory"""
        method = env.get('REQUEST_METHOD', 'GET').upper()

        if method in _browser_methods:
            if (method == 'POST' and
                env.get('CONTENT_TYPE', '').startswith('text/xml')
                ):
                request = XMLRPCRequest(input_stream, output_steam, env)
                request.setPublication(self._xmlrpc)
            else:
                request = BrowserRequest(input_stream, output_steam, env)
                request.setPublication(self._brower)
        else:
            request = HTTPRequest(input_stream, output_steam, env)
            request.setPublication(self._http)

        return request

realize = HTTPPublicationRequestFactory
