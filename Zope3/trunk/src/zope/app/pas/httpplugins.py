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
from zope.interface import implements, Interface
from zope.publisher.interfaces.http import IHTTPRequest
from zope.schema import TextLine 

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
    {'login': u'mgr', 'password': u'mgrpw'}

    Make sure we return `None`, if no authentication header has been
    specified.

    >>> extractor.extractCredentials(TestRequest()) is None
    True

    Also, this extractor can *only* handle basic authentication.

    >>> request = TestRequest({'HTTP_AUTHORIZATION': 'foo bar'})
    >>> extractor.extractCredentials(TestRequest()) is None
    True
    """
    implements(IExtractionPlugin)

    def extractCredentials(self, request):
        if request._auth:
            if request._auth.lower().startswith(u'basic '):
                credentials = request._auth.split()[-1]
                login, password = base64.decodestring(credentials).split(':')
                return {'login': login.decode('utf-8'),
                        'password': password.decode('utf-8')}
        return None


class IHTTPBasicAuthRealm(Interface):
    """HTTP Basic Auth Realm

    Represents the realm string that is used during basic HTTP authentication
    """

    realm = TextLine(title=u'Realm',
                     description=u'HTTP Basic Authentication Realm',
                     required=True,
                     default=u'Zope3')
    

class HTTPBasicAuthChallenger(Persistent, Contained):
    """A Basic HTTP Authentication Challenge Plugin

    >>> challenger = HTTPBasicAuthChallenger()

    The challenger adds its challenge to the HTTP response.

    >>> from zope.publisher.browser import TestRequest
    >>> request = TestRequest()
    >>> response = request.response
    >>> challenger.challenge(request, response)
    True
    >>> response._status
    401
    >>> response.getHeader('WWW-Authenticate', literal=True)
    'basic realm=Zope3'

    The challenger only works with HTTP requests.

    >>> from zope.publisher.base import TestRequest
    >>> request = TestRequest('/')
    >>> response = request.response
    >>> challenger.challenge(request, response) is None
    True
    """
    implements(IChallengePlugin, IHTTPBasicAuthRealm)

    realm = 'Zope3'
    protocol = 'http auth'

    def challenge(self, request, response):
        if not IHTTPRequest.providedBy(request):
            return None
        response.setHeader("WWW-Authenticate", "basic realm=%s" % self.realm,
                           literal=True)
        response.setStatus(401)
        return True
