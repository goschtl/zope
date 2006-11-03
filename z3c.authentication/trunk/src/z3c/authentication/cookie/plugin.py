##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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

import transaction
import persistent
import zope.interface
from urllib import urlencode

from zope.publisher.interfaces.http import IHTTPRequest
from zope.traversing.browser.absoluteurl import absoluteURL

from zope.app.component import hooks
from zope.app.container.contained import Contained
from zope.app.session.interfaces import ISession
from zope.app.authentication.session import SessionCredentialsPlugin
from z3c.authentication.cookie import interfaces


class CookieCredentials(persistent.Persistent, Contained):
    """Credentials class for use with sessions.

    A session credential is created with a login and a password:

      >>> cred = CookieCredentials('scott', 'tiger')

    Logins are read using getLogin:
      >>> cred.getLogin()
      'scott'

    and passwords with getPassword:

      >>> cred.getPassword()
      'tiger'

    """
    zope.interface.implements(interfaces.ICookieCredentials)

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def getLogin(self): return self.login

    def getPassword(self): return self.password

    def __str__(self): return self.getLogin() + ':' + self.getPassword()


class CookieCredentialsPlugin(SessionCredentialsPlugin):
    """A credentials plugin that uses Zope sessions to get/store credentials.

    To illustrate how a session plugin works, we'll first setup some session
    machinery:

    >>> from zope.publisher.tests.httprequest import TestRequest
    >>> from z3c.authentication.cookie import testing
    >>> testing.sessionSetUp()

    This lets us retrieve the same session info from any test request, which
    simulates what happens when a user submits a session ID as a cookie.

    We also need a session plugin:

    >>> plugin = CookieCredentialsPlugin()

    A session plugin uses an ISession component to store the last set of
    credentials it gets from a request. Credentials can be retrieved from
    subsequent requests using the session-stored credentials.

    Our test environment is initially configured without credentials:

    >>> request = TestRequest()
    >>> print plugin.extractCredentials(request)
    None

    We must explicitly provide credentials once so the plugin can store
    them in a session:

    >>> request = TestRequest(login='scott', password='tiger', autologin='on')
    >>> plugin.extractCredentials(request)
    {'login': 'scott', 'password': 'tiger'}

    Check if we get the initial login session flag:

    >>> session = ISession(request)
    >>> sessionData = session[interfaces.SESSION_KEY]
    >>> sessionData.get('initialLogin', False)
    True

    Subsequent requests now have access to the credentials even if they're
    not explicitly in the request:

    >>> plugin.extractCredentials(TestRequest())
    {'login': 'scott', 'password': 'tiger'}

    See if the initial login session is still there:

    >>> sessionData.get('initialLogin', False)
    True

    The initial login session didn't get set because we didn't use the 
    autologin field. Let's try use the autologin field and check the session.

    >>> request = TestRequest(login='scott', password='tiger', autologin='on')
    >>> sessionData.get('initialLogin', False)
    True

    We can always provide new credentials explicitly in the request:

    >>> plugin.extractCredentials(TestRequest(
    ...     login='harry', password='hirsch'))
    {'login': 'harry', 'password': 'hirsch'}

    and these will be used on subsequent requests:

    >>> plugin.extractCredentials(TestRequest())
    {'login': 'harry', 'password': 'hirsch'}

    We can also change the fields from which the credentials are extracted:
    
    >>> plugin.loginfield = "my_new_login_field"
    >>> plugin.passwordfield = "my_new_password_field"
      
    Now we build a request that uses the new fields:
    
    >>> request = TestRequest(my_new_login_field='luke', 
    ...     my_new_password_field='the_force')
      
    The plugin now extracts the credentials information from these new fields:
    
    >>> plugin.extractCredentials(request)
    {'login': 'luke', 'password': 'the_force'}

    Finally, we clear the session credentials using the logout method:

    >>> plugin.logout(TestRequest())
    True
    >>> print plugin.extractCredentials(TestRequest())
    None

    After a logout the initial login session flag must be disabled:
    
    >>> sessionData.get('initialLogin', False)
    False

    """
    zope.interface.implements(interfaces.ICookieCredentialsPlugin)

    loginpagename = 'loginForm.html'
    loginfield = 'login'
    passwordfield = 'password'
    autologinfield = 'autologin'

    def extractCredentials(self, request):
        """Extracts credentials from a session if they exist."""
        if not IHTTPRequest.providedBy(request):
            return None
        session = ISession(request, None)
        sessionData = session.get(interfaces.SESSION_KEY)
        login = request.get(self.loginfield, None)
        password = request.get(self.passwordfield, None)
        autologin = request.get(self.autologinfield, None)
        credentials = None
        initialLogin = False

        if login and password:
            credentials = CookieCredentials(login, password)
            # first or relogin login
            if autologin:
                credentials.autologin = True
            else:
                credentials.autologin = False
            initialLogin = True
        elif not sessionData:
            # go away if no available session and no login try
            return None
        # not first access on portal
        sessionData = session[interfaces.SESSION_KEY]
        if credentials:
            # first login or relogin
            sessionData['credentials'] = credentials
        else:
            # already logged in or not
            credentials = sessionData.get('credentials', None)
        if not credentials:
            # not already logged in
            return None
        
        if initialLogin:
            # set a marker for the initial login in the session
            sessionData['initialLogin'] = True
            # and do login
            return self.__doLogin(credentials)
        
        # all below this is a ongoing login or a autologin
        initialLoginSession = sessionData.get('initialLogin', False)
        if credentials.autologin == False and not initialLoginSession:
            # do not login if autologin is disabled and first login session 
            # is not set. 
            return None

        # ongoing login or active autologin
        return self.__doLogin(credentials)

    def __doLogin(self, credentials):
        return {'login': credentials.getLogin(),
                'password': credentials.getPassword()}

    def logout(self, request):
        """Performs logout by clearing session data credentials."""
        if not IHTTPRequest.providedBy(request):
            return False

        sessionData = ISession(request)[interfaces.SESSION_KEY]
        sessionData['credentials'] = None
        sessionData['initialLogin'] = False
        transaction.commit()
        return True
