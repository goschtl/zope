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
""" Implementations of the session-based and cookie-based extractor and
    challenge plugins.

$Id$
"""

from zope.interface import implements
from persistent import Persistent
from zope.app.component import hooks
from zope.app.container.contained import Contained
from zope.app.traversing.browser.interfaces import IAbsoluteURL
from zope.app import zapi
from zope.app.session.interfaces import ISession

from zope.app.pas.interfaces import IExtractionPlugin, IChallengePlugin

class SessionExtractor(Persistent, Contained):
    """ session-based credential extractor.

        Extract the credentials that are referenced in the
        request by looking them up in the session.

        >>> from zope.app.session.session import RAMSessionDataContainer
        >>> from zope.app.session.session import Session
        >>> from tests import sessionSetUp, createTestRequest

        >>> sessionSetUp(RAMSessionDataContainer)
        >>> se = SessionExtractor()

        No credentials available:
        >>> request = createTestRequest()
        >>> se.extractCredentials(request)

        If the session does not contain the credentials check
        the request for form variables.
        >>> request = createTestRequest(username='scott', password='tiger')

        >>> se.extractCredentials(request)
        {'username': 'scott', 'password': 'tiger'}

        >>> request = createTestRequest()
        >>> sessionData = Session(request)['pas_credentials']
        >>> sessionData['username'] = 'scott'
        >>> sessionData['password'] = 'tiger'
        >>> se.extractCredentials(request)
        {'username': 'scott', 'password': 'tiger'}
     """
    implements(IExtractionPlugin)

    def extractCredentials(self, request):
        sessionData = ISession(request)['pas_credentials']
        if not sessionData:
            un = request.get('username', None)
            pw = request.get('password', None)
            if un and pw:
                sessionData['username'] = un
                sessionData['password'] = pw
            else:
                return None
        return {'username': sessionData['username'],
                'password': sessionData['password']}


class FormChallenger(Persistent, Contained):
    """ Query the user for credentials using a browser form.

        First we need a request and a response.

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()
        >>> response = request.response

        Then we create a FormAuthChallenger and call it.
        >>> fc = FormChallenger()
        >>> fc.challenge(request, response)
        True

        The response's headers should now contain the URL to redirect to.
        >>> headers = response.getHeaders()
        >>> headers['Location']
        'http://127.0.0.1'

    """

    implements(IChallengePlugin)

    def challenge(self, request, response):
        """ Response shuold redirect to login page cause Credebtials
            could not have been extracted.
        """
        site = hooks.getSite()
        #url = zapi.getView(site, zapi.name(site), request, providing=IAbsoluteURL,
        #                   context=site)
        url = request.getApplicationURL()
        response.redirect(url)

        return True
