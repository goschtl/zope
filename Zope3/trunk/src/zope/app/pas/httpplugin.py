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
"""PAS plugins related to HTTP

$Id$
"""
__docformat__ = "reStructuredText"
import base64
from persistent import Persistent
from zope.interface import implements

from zope.app.container.contained import Contained
from interfaces import IExtractionPlugin, IChallengePlugin


class HTTPBasicAuthExtractor(Persistent, Contained):
    """A Basic HTTP Authentication Crendentials Extraction Plugin

    First we need to create a request that contains some credentials.
    
    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest(
    ...     environ={'HTTP_AUTHORIZATION': u'Basic bWdyOm1ncnB3'})

    Now create the extraction plugin and get the credentials.

    >>> extractor = HTTPBasicAuthExtractor()
    >>> extractor.extractCredentials(request)
    (u'mgr', u'mgrpw')

    Make sure we return `None`, if no authentication header has been
    specified.

    >>> extractor.extractCredentials(TestRequest()) is None
    True

    Also, this extractor can *only* hadle basic authentication.

    >>> request = TestRequest({'HTTP_AUTHORIZATION': 'foo bar'})
    >>> extractor.extractCredentials(TestRequest()) is None
    True
    """
    implements(IExtractionPlugin)

    def extractCredentials(self, request):
        if request._auth:
            if request._auth.lower().startswith(u'basic '):
                credentials = request._auth.split()[-1] 
                username, password = base64.decodestring(credentials).split(':')
                return username.decode('utf-8'), password.decode('utf-8')


class HTTPBasicAuthChallenger(Persistent, Contained):
    """A Basic HTTP Authentication Challenge Plugin

    """
    implements(IChallengePlugin)

    realm = 'Zope 3'
    
    def challenge(self, requests, response):
        response.setHeader("WWW-Authenticate", "basic realm=%s" %self.realm,
                           True)
        response.setStatus(401)
        return True
