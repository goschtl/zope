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

from zope.interface import implements, Interface
from zope.schema import TextLine
from persistent import Persistent
from zope.app.component import hooks
from zope.app.container.contained import Contained
from zope.app.traversing.browser.absoluteurl import absoluteURL
from zope.app import zapi
from zope.app.session.interfaces import ISession, IClientId
import transaction 
import transaction 
from urllib import urlencode

from zope.app.pas.interfaces import IExtractionPlugin, IChallengePlugin


class ISessionCredentials(Interface):
    """ Interface for storing and accessing credentials in a session.

        We use a real class with interface here to prevent unauthorized
        access to the credentials.
    """

    def __init__(login, password):
        pass

    def getLogin():
        """Return login name."""

    def getPassword():
        """Return password."""


class SessionCredentials:
    """ Credentials class for use with sessions.

        >>> cred = SessionCredentials('scott', 'tiger')
        >>> cred.getLogin()
        'scott'
        >>> cred.getPassword()
        'tiger'
    """
    implements(ISessionCredentials)

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def getLogin(self): return self.login

    def getPassword(self): return self.password

    def __str__(self): return self.getLogin() + ':' + self.getPassword()


class SessionExtractor(Persistent, Contained):
    """ session-based credential extractor.

        Extract the credentials that are referenced in the
        request by looking them up in the session.

        >>> from zope.app.session.session import RAMSessionDataContainer
        >>> from zope.app.session.session import Session
        >>> from tests import sessionSetUp, TestRequest

        >>> sessionSetUp(RAMSessionDataContainer)
        >>> se = SessionExtractor()


        Start: No credentials available
        >>> request = TestRequest()
        >>> se.extractCredentials(request) is None
        True

        Credentials provided by submitting login form:
        If the session does not contain the credentials check
        the request for form variables and store the credentials in
        the session.
        >>> request = TestRequest(login='scott', password='tiger')
        >>> se.extractCredentials(request)
        {'login': 'scott', 'password': 'tiger'}

        After login the credentials are stored in the session.
        (The sessionSetUp() method ensures that in this test the request
        always gets the same client id so we get the same session data.)
        >>> request = TestRequest()
        >>> se.extractCredentials(request)
        {'login': 'scott', 'password': 'tiger'}

        Magic logout command in URL forces log out by deleting the
        credentials from the session.
        >>> request = TestRequest(authrequest='logout')
        >>> se.extractCredentials(request) is None
        True
        >>> Session(request)['pas']['credentials'] is None
        True
     """
    implements(IExtractionPlugin)

    def extractCredentials(self, request):
        """ return credentials from session, request or None """
        sessionData = ISession(request)['pas']
        credentials = sessionData.get('credentials', None)
        if not credentials:
            # check for form data
            login = request.get('login', None)
            password = request.get('password', None)
            if login and password:
                credentials = SessionCredentials(login, password)
                sessionData['credentials'] = credentials
            else:
                return None
        authrequest = request.get('authrequest', None)
        if authrequest == 'logout':
            sessionData['credentials'] = None
            transaction.commit()
            return None
        return {'login': credentials.getLogin(),
                'password': credentials.getPassword()}



class IFormChallengerLoginPageName(Interface):
    """HTTP Basic Auth Realm

    Represents the realm string that is used during basic HTTP authentication
    """

    loginpagename = TextLine(title=u'loginpagename',
                     description=u'Name of the login form used by challenger',
                     required=True,
                     default=u'loginForm.html')


class FormChallenger(Persistent, Contained):
    """ Query the user for credentials using a browser form.

        First we need a request and a response.

        >>> from zope.app.tests.setup import placefulSetUp
        >>> site = placefulSetUp(True)


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
        'http://127.0.0.1/@@loginForm.html?camefrom=http%3A%2F%2F127.0.0.1'

    """

    implements(IChallengePlugin, IFormChallengerLoginPageName)
    
    loginpagename = 'loginForm.html'

    def challenge(self, request, response):
        """ Response shuold redirect to login page cause Credebtials
            could not have been extracted.
        """
        site = hooks.getSite()
        
        camefrom = request.getURL()

        url = '%s/@@%s?%s' % (absoluteURL(site, request),
                              self.loginpagename,
                              urlencode({'camefrom' :camefrom}))
        response.redirect(url)

        return True
