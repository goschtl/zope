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

$Id: session.py 80262 2007-09-27 23:47:04Z srichter $
"""
__docformat__ = 'restructuredtext'

import transaction
from persistent import Persistent
from urllib import urlencode
from time import time

from zope.interface import implements, Interface
from zope.schema import TextLine, Int, Choice
from zope.component import getUtility
from zope.publisher.interfaces.http import IHTTPRequest
from zope.session.interfaces import ISession
from zope.traversing.browser.absoluteurl import absoluteURL

from zope.app.component import hooks
from zope.app.container.contained import Contained
from zope.app.authentication.interfaces import ISessionCredentialsPlugin
from zope.app.authentication.interfaces import ICredentialsPlugin

from interfaces import IPasswordManager

class ISessionCredentials(Interface):
    """ Interface for storing and accessing credentials in a session.

        We use a real class with interface here to prevent unauthorized
        access to the credentials.
    """

    def __init__(login, password, ip=None, domain=None):
        pass

    def getLogin():
        """Return login name."""

    def getPassword():
        """Return password."""

    def getIP():
        """Return the IP address of the remote address from which the login session
        originated (IP address is a string)."""

    def getDomain():
        """Return the domain. The presence of the domain is optional and predicated
        by the layout of the login form.."""

    def getRequestAnnotations():
        """Provides a mechanism for passing information from the login form"""

    def getExtractTime():
        """Returns the time of the original login"""

    def getAccessTime():
        """Return the time of the last access - can be used to compute idle time"""

    def getPasswordManager():
        """Return the class used for encrypting the password"""

    def isExpired(timeout):
        """Returns True if the credentials have expired based on the timeout
        parameter (specified in minutes)"""

class SessionCredentials(object):
    """Credentials class for use with sessions.

    A session credential is created with a login and a password:

      >>> cred = SessionCredentials('scott', 'tiger')

    Logins are read using getLogin:
      >>> cred.getLogin()
      'scott'

    and passwords with getPassword:

      >>> cred.getPassword()
      'tiger'

    """
    implements(ISessionCredentials)

    # Included these here for migration. 
    ip=None
    domain=None
    request_annotations=None
    extractTime=None
    accessTime=None
    passwordManager=None

    def __init__(self, login, password, ip=None, domain=None, request_annotations=None, passwordManager=None):
        self.login = login
        if passwordManager:
            self.password = passwordManager.encodePassword(password)
        else:
            self.password = password
        self.ip = ip
        self.domain = domain
        self.request_annotations = request_annotations
        self.passwordManager=passwordManager

        self.extractTime = time()
        self.accessTime = 0

    def getLogin(self): return self.login

    def getPassword(self): return self.password

    def getIP(self): return self.ip

    def getDomain(self): return self.domain

    def getRequestAnnotations(self): return self.request_annotations

    def getExtractTime(self): return self.extractTime

    def getAccessTime(self): return self.accessTime

    def getPasswordManager(self): return self.passwordManager

    def isExpired(self, timeout):
        """Determine whether the session is timed out. If there is no
        idletime out set, then the self.accessTime value remains at 0"""
        if timeout <= 0: return False
        timeNow = time()
        if self.accessTime == 0:
            self.bumpAccessTime(timeNow)
            return False
        return (timeNow // 60 - self.accessTime // 60) > timeout

    def bumpAccessTime(self, timeNow):
        """Increment the access time if necessary"""
        if int(timeNow // 60) > int(self.accessTime // 60):
            self.accessTime = timeNow

    def __str__(self):
        if self.domain:
            return self.getDomain() + ':' + self.getLogin() + ':' + self.getPassword()
        else:
            return self.getLogin() + ':' + self.getPassword()


class IBrowserFormChallenger(Interface):
    """A challenger that uses a browser form to collect user credentials."""

    loginpagename = TextLine(
        title=u'Loginpagename',
        description=u"""Name of the login form used by challenger.

        The form must provide 'login' and 'password' input fields.
        """,
        default=u'loginForm.html')

    domainfield = TextLine(
        title=u'Domainfield (only used if active on login page see loginform.pt)',
        description=u"Field on the login page in which the login domain is provided if login domains are used.",
        default=u"domain")

    loginfield = TextLine(
        title=u'Loginfield',
        description=u"Field of the login page in which is looked for the login user name.",
        default=u"login")

    passwordfield = TextLine(
        title=u'Passwordfield',
        description=u"Field of the login page in which is looked for the password.",
        default=u"password")

    idleExpiry = TextLine(
        title=u'Expiry timeout in minutes for idle sessions (0 for unused)',
        description=u"Expiry timeout in minutes for idle sessions.",
        default=u"0")

    passwordManagerName = Choice(
        title=u'Password Manager Class',
        description=u"Password Manager Class.",
        vocabulary=u"Password Manager Names")

class SessionCredentialsPlugin(Persistent, Contained):
    """A credentials plugin that uses Zope sessions to get/store credentials.

    To illustrate how a session plugin works, we'll first setup some session
    machinery:

      >>> from zope.session.session import RAMSessionDataContainer
      >>> from tests import sessionSetUp
      >>> sessionSetUp(RAMSessionDataContainer)

    This lets us retrieve the same session info from any test request, which
    simulates what happens when a user submits a session ID as a cookie.

    We also need a session plugin:

      >>> plugin = SessionCredentialsPlugin()

    A session plugin uses an ISession component to store the last set of
    credentials it gets from a request. Credentials can be retrieved from
    subsequent requests using the session-stored credentials.

    Our test environment is initially configured without credentials:

      >>> from tests import sessionSetUp
      >>> from zope.publisher.browser import TestRequest
      >>> request = TestRequest()
      >>> print plugin.extractCredentials(request)
      None

    We must explicitly provide credentials once so the plugin can store
    them in a session:

      >>> request = TestRequest(login='scott', password='tiger')
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['login'] == 'scott'
      True
      >>> credentials['password'] == 'tiger'
      True

    Subsequent requests now have access to the credentials even if they're
    not explicitly in the request:

      >>> credentials = plugin.extractCredentials(TestRequest()) 
      >>> credentials['login'] == 'scott'
      True
      >>> credentials['password'] == 'tiger'
      True

    We can always provide new credentials explicitly in the request:

      >>> credentials = plugin.extractCredentials(TestRequest(
      ...     login='harry', password='hirsch'))
      >>> credentials['login'] == 'harry'
      True
      >>> credentials['password'] == 'hirsch'
      True

    and these will be used on subsequent requests:

      >>> credentials = plugin.extractCredentials(TestRequest())
      >>> credentials['login'] == 'harry'
      True
      >>> credentials['password'] == 'hirsch'
      True

    We can also change the fields from which the credentials are extracted:

      >>> plugin.loginfield = "my_new_login_field"
      >>> plugin.passwordfield = "my_new_password_field"

    Now we build a request that uses the new fields:

      >>> request = TestRequest(my_new_login_field='luke', my_new_password_field='the_force')

    The plugin now extracts the credentials information from these new fields:

      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['login'] == 'luke'
      True
      >>> credentials['password'] == 'the_force'
      True

    Set these fields back to their standard names.

      >>> plugin.loginfield = "login"
      >>> plugin.passwordfield = "password"

    The credentials collector also collects and returns a domain, if it is present,
    the IP address of the request machine and the time of the credentials extraction.

      >>> request = TestRequest(login='scott', password='tiger', domain='company',
      ...         REMOTE_ADDR='127.0.0.1')
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['domain'] == 'company'
      True
      >>> credentials['ip'] == '127.0.0.1'
      True
      >>> request.response.getCookie('login.domain')['value']
      'company'

    And these are also stored in the session data store.

      >>> credentials = plugin.extractCredentials(TestRequest()) 
      >>> credentials['domain'] == 'company'
      True
      >>> credentials['ip'] == '127.0.0.1'
      True

    The HTTP_X_FORWARDED_FOR header overrides the REMOTE_ADDR header

      >>> request = TestRequest(login='scott', password='tiger', domain='company',
      ...         REMOTE_ADDR='127.0.0.1', HTTP_X_FORWARDED_FOR='192.168.0.1')
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['ip'] == '192.168.0.1'
      True

    When the user is logging in the 'logging_in' return value is set to True,
    otherwise it is set to False.

      >>> request = TestRequest(login='scott', password='tiger')
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['logging_in'] == True
      True
      >>> request = TestRequest()
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['logging_in'] == False
      True

    A password manager can be configured. The name must match the name of a 
    utility in the global site manager.
        
      >>> class NullManager:
      ...     implements(IPasswordManager)
      ...     def encodePassword(self, password):
      ...         return password.lower()
      ...     def checkPassword(self, storedPassword, password):
      ...         return storedPassword == self.encodePassword(password)
        
      >>> from zope.app.authentication.interfaces import IPasswordManager
      >>> manager = NullManager()
      >>> from zope.component import getGlobalSiteManager
      >>> gsm = getGlobalSiteManager()
      >>> gsm.registerUtility(manager, IPasswordManager, 'manager')
      >>> plugin.passwordManagerName = "manager"

    When an encrypter is configured, the password will be encrypted, and the
    encrypter will be returned.

      >>> request = TestRequest(login='scott', password='TIGER')
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['password'] == 'tiger'
      True
      >>> credentials['passwordManager'].encodePassword('TIGER') == credentials['password']
      True

    The extraction time is recorded. It is returned with the credentials.

      >>> import time
      >>> request = TestRequest(login='scott', password='TIGER')
      >>> credentials = plugin.extractCredentials(request) 
      >>> timeNow = time.time()
      >>> credentials['extractTime'] < timeNow
      True
      >>> credentials['extractTime'] > timeNow - 2.0
      True
      >>> extracted_time = credentials['extractTime']
      >>> request = TestRequest()
      >>> credentials = plugin.extractCredentials(request) 
      >>> extracted_time == credentials['extractTime']
      True

    Access time is recorded if there is an idle expiry timeout.

      >>> request = TestRequest(login='scott', password='TIGER')
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['accessTime'] == 0
      True
      >>> plugin.idleExpiry = 30
      >>> request = TestRequest()
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['accessTime'] != 0
      True

    When the credentials time out, they will no longer be returned

      >>> request = TestRequest()
      >>> session = ISession(request)
      >>> sessionData = session.get(
      ...     'zope.app.authentication.browserplugins')
      >>> credentials = sessionData.get('credentials', None)
      >>> credentials.accessTime = 1
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials == None
      True

    When overrides are provided as a parameter to the extractCredentials,
    they are used in preference to the data on the request.

      >>> request = TestRequest(login='r_login', password='r_pass',
      ...       REMOTE_ADDR='r_ip', domain='r_domain')
      >>> overrides = {}
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['login'] == 'r_login'
      True
      >>> credentials['password'] == 'r_pass'
      True
      >>> credentials['ip'] == 'r_ip'
      True
      >>> credentials['domain'] == 'r_domain'
      True
      >>> overrides = {'login':'o_login', 'password':'o_pass',
      ...       'ip':'o_ip', 'domain':'o_domain'}
      >>> credentials = plugin.extractCredentials(request, overrides)
      >>> credentials['login'] == 'o_login'
      True
      >>> credentials['password'] == 'o_pass'
      True
      >>> credentials['ip'] == 'o_ip'
      True
      >>> credentials['domain'] == 'o_domain'
      True

    If the request annotations are attached to the request, then they
    are stored and passed on with the credentials.

      >>> request = TestRequest(login='r_login', password='r_pass')
      >>> request.annotations = 'ANNOTATED'
      >>> credentials = plugin.extractCredentials(request) 
      >>> credentials['request-annotations']
      'ANNOTATED'

    Finally, we clear the session credentials using the logout method:

      >>> request = TestRequest(login='scott', password='TIGER')
      >>> credentials = plugin.extractCredentials(request) 
      >>> plugin.logout(TestRequest())
      True
      >>> print plugin.extractCredentials(TestRequest())
      None

    """
    implements(ICredentialsPlugin, IBrowserFormChallenger, ISessionCredentialsPlugin)

    loginpagename = 'loginForm.html'
    loginfield = 'login'
    passwordfield = 'password'
    domainfield = 'domain'
    idleExpiry = 0
    passwordManagerName = None

    def extractCredentials(self, request, overrides=None):
        """Extracts credentials from a session if they exist."""

        if not IHTTPRequest.providedBy(request):
            return None

        session = ISession(request)
        sessionData = session.get(
            'zope.app.authentication.browserplugins')

        (login, password, domain, ip) = (None, None, None, None)
        credentials = None
        logging_in = False

        if overrides:
            login = overrides.get('login', None)
            password = overrides.get('password', None)
            ip = overrides.get('ip', None)
            domain = overrides.get('domain', None)

        login = login or request.get(self.loginfield, None)
        password = password or request.get(self.passwordfield, None)
        domain = domain or request.get(self.domainfield, None)
        ip = ip or request.environment.get('HTTP_X_FORWARDED_FOR', None)
        ip = ip or request.environment.get('REMOTE_ADDR', None)

        if login and password:
            credentials = SessionCredentials(login, password,
                ip=ip, domain=domain, request_annotations = request.annotations,
                passwordManager = self.passwordManager)
            if IHTTPRequest.providedBy(request):
                self._update_cookie(request, credentials)
            logging_in = True
                    
        elif not sessionData:
            return None
        sessionData = session[
            'zope.app.authentication.browserplugins']
        if credentials:
            sessionData['credentials'] = credentials
        else:
            credentials = sessionData.get('credentials', None)
            if not credentials:
                return None
            if credentials.isExpired(self.idleExpiry):
                return None
        return {'login': credentials.getLogin(),
                'password': credentials.getPassword(),
                'ip': credentials.getIP(),
                'domain': credentials.getDomain(),
                'logging_in': logging_in,
                'request-annotations': credentials.getRequestAnnotations(),
                'extractTime': credentials.getExtractTime(),
                'accessTime': credentials.getAccessTime(),
                'passwordManager': credentials.getPasswordManager(),
                }

    def _update_cookie(self, request, credentials):
        """Sets a cookie to record the login domain"""
        if credentials:
            domain = credentials.getDomain()
            if domain and (request.cookies.get('login.domain') != domain):
                request.response.setCookie(
                    'login.domain', domain,
                    expires = 'Wed, 01-Jan-3000 00:00:00 GMT',
                )
            return credentials

    @property
    def passwordManager(self):
        """Return the Password Manager object in used for encrypting passwords"""
        if not self.passwordManagerName:
            return None
        try:
            return self._v_cache[self.passwordManagerName]
        except:
            pass
        manager = getUtility(IPasswordManager, self.passwordManagerName, context = self.__parent__)
        if not hasattr(self, '_v_cache'):
            self._v_cache = {}
        try:
            self._v_cache[self.passwordManagerName] = manager
        except AttributeError:
            self._v_cache = {self.passwordManagerName: manager}
        return manager

    def challenge(self, request):
        """Challenges by redirecting to a login form.

        To illustrate, we'll create a test request:

          >>> from zope.publisher.browser import TestRequest
          >>> request = TestRequest()

        and confirm its response's initial status and 'location' header:

          >>> request.response.getStatus()
          599
          >>> request.response.getHeader('location')

        When we issue a challenge using a session plugin:

          >>> plugin = SessionCredentialsPlugin()
          >>> plugin.challenge(request)
          True

        we get a redirect:

          >>> request.response.getStatus()
          302
          >>> request.response.getHeader('location')
          'http://127.0.0.1/@@loginForm.html?camefrom=%2F'

        The plugin redirects to the page defined by the loginpagename
        attribute:

          >>> plugin.loginpagename = 'mylogin.html'
          >>> plugin.challenge(request)
          True
          >>> request.response.getHeader('location')
          'http://127.0.0.1/@@mylogin.html?camefrom=%2F'

        It also provides the request URL as a 'camefrom' GET style parameter.
        To illustrate, we'll pretend we've traversed a couple names:

          >>> env = {
          ...     'REQUEST_URI': '/foo/bar/folder/page%201.html?q=value',
          ...     'QUERY_STRING': 'q=value'
          ...     }
          >>> request = TestRequest(environ=env)
          >>> request._traversed_names = [u'foo', u'bar']
          >>> request._traversal_stack = [u'page 1.html', u'folder']
          >>> request['REQUEST_URI']
          '/foo/bar/folder/page%201.html?q=value'

        When we challenge:

          >>> plugin.challenge(request)
          True

        We see the 'camefrom' points to the requested URL:

          >>> request.response.getHeader('location') # doctest: +ELLIPSIS
          '.../@@mylogin.html?camefrom=%2Ffoo%2Fbar%2Ffolder%2Fpage+1.html%3Fq%3Dvalue'

        This can be used by the login form to redirect the user back to the
        originating URL upon successful authentication.
        """
        if not IHTTPRequest.providedBy(request):
            return False

        site = hooks.getSite()
        # We need the traversal stack to complete the 'camefrom' parameter
        stack = request.getTraversalStack()
        stack.reverse()
        # Better to add the query string, if present
        query = request.get('QUERY_STRING')

        camefrom = '/'.join([request.getURL(path_only=True)] + stack)
        if query:
            camefrom = camefrom + '?' + query
        url = '%s/@@%s?%s' % (absoluteURL(site, request),
                              self.loginpagename,
                              urlencode({'camefrom': camefrom}))
        request.response.redirect(url)
        return True

    def logout(self, request):
        """Performs logout by clearing session data credentials."""
        if not IHTTPRequest.providedBy(request):
            return False

        sessionData = ISession(request)[
            'zope.app.authentication.browserplugins']
        sessionData['credentials'] = None
        transaction.commit()
        return True

    def clearPasswordManager(self, request):
        """If there is a mistmatch between the encryption used by the
        principal and the encryption used for the session, then there
        is no possible recovery. Trigger this function, which will 
        clear the encryption used for the session. Clear text passwords
        can flow through to the principal machinery, which can then use
        it's own configured password manager to do the encryption.
        
        To demonstrate, first set up a plugin with a passwordManager

          >>> from zope.publisher.browser import TestRequest

          >>> from zope.session.session import RAMSessionDataContainer
          >>> from tests import sessionSetUp
          >>> sessionSetUp(RAMSessionDataContainer)

          >>> plugin = SessionCredentialsPlugin()

          >>> class NullManager:
          ...     implements(IPasswordManager)
          ...     def encodePassword(self, password):
          ...         return password.lower()
          ...     def checkPassword(self, storedPassword, password):
          ...         return storedPassword == self.encodePassword(password)

          >>> from zope.app.authentication.interfaces import IPasswordManager
          >>> manager = NullManager()
          >>> from zope.component import getGlobalSiteManager
          >>> gsm = getGlobalSiteManager()
          >>> gsm.registerUtility(manager, IPasswordManager, 'manager')
          >>> plugin.passwordManagerName = "manager"
                
          >>> request = TestRequest(login='scott', password='TIGER')
          >>> credentials = plugin.extractCredentials(request) 
          >>> credentials['password']
          'tiger'

        Next, clear the password manager

          >>> plugin.clearPasswordManager(request)

        The cached credentials are cleared. The password was encrypted so that it
        is unusable.

          >>> plugin.extractCredentials(TestRequest())  == None
          True

        Subsequent login attempts will return unencrypted credentials.

          >>> credentials = plugin.extractCredentials(request) 
          >>> credentials['passwordManager'] == None
          True
          >>> credentials['password']
          'TIGER'

        """
            
        # FORCE THE CHANGE - TODO: LOG, TODO: Work with published interface
        #print 'clearPasswordManager'

        self.passwordManagerName = None

        session = ISession(request)
        sessionData = session.get(
            'zope.app.authentication.browserplugins')
        del sessionData['credentials']

