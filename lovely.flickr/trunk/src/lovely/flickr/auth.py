##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""This module implements the flickr.auth namespace

http://www.flickr.com/services/api/

$Id$
"""
__docformat__ = "reStructuredText"
import urllib
import zope.interface
from zope.schema import fieldproperty
from lovely.flickr import interfaces, flickr
from zope.testbrowser import browser
from mechanize import Browser


class _InternalWebBrowser(Browser):
    """A special type of mechanize browser.

    This is unfortunately necessary, because the default setup pf the
    mechanize browser does not work with the "Yahoo! Sin In" page. Oh well.

    We do not provide '_http_error' in ``default_others`` and '_refresh' in
    ``default_features``.
    """
    default_others = ['_http_error', '_http_request_upgrade',
                      '_http_default_error']
    default_features = ['_redirect', '_cookies', '_referer', '_refresh',
                        '_equiv', '_basicauth', '_digestauth', '_seek' ]

    def activateRefreshHandler(self):
        refresh_handler = self.handler_classes['_refresh']()
        self._ua_handlers['_refresh'] = refresh_handler
        self.add_handler(refresh_handler)
        self.set_handle_refresh(refresh_handler)

    def deactivateRefreshHandler(self):
        handler = self._ua_handlers['_refresh']
        self._replace_handler('_refresh')
        del self._ua_handlers['_refresh']


class User(object):
    zope.interface.implements(interfaces.IUser)

    nsid = fieldproperty.FieldProperty(interfaces.IUser['nsid'])
    username = fieldproperty.FieldProperty(interfaces.IUser['username'])
    fullname = fieldproperty.FieldProperty(interfaces.IUser['fullname'])

    def __init__(self, nsid, username, fullname=None):
        self.nsid = nsid
        self.username = username
        if fullname is not None:
            self.fullname = fullname

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        args = dict([
            (name, field.fromUnicode(unicode(element.get(name))))
            for name, field in zope.schema.getFields(interfaces.IUser).items()
            ])
        return User(**args)

    def __repr__(self):
        return '<%s %r - %r>' %(self.__class__.__name__,
                                self.username, self.fullname)


class Auth(object):
    zope.interface.implements(interfaces.IAuth)

    token = fieldproperty.FieldProperty(interfaces.IAuth['token'])
    perms = fieldproperty.FieldProperty(interfaces.IAuth['perms'])
    user = fieldproperty.FieldProperty(interfaces.IAuth['user'])

    def __init__(self, token, perms, user):
        self.token = token
        self.perms = perms
        self.user = user

    @classmethod
    def fromElement(self, element):
        """See interfaces.IBaseFlickrObject"""
        token = unicode(element.find('token').text)
        perms = [unicode(perm.strip())
                 for perm in element.find('perms').text.split(',')]
        user = User.fromElement(element.find('user'))
        return Auth(token, perms, user)

    def __repr__(self):
        return '<%s %s>' %(self.__class__.__name__, self.token)


class APIAuth(flickr.APIFlickr):
    """This class provides a pythonic interface to the ``flickr.auth``
       namespace.
    """
    zope.interface.implements(interfaces.IAPIAuth)

    # This can be turned off in tests when dealing with stub implementations
    _authenticate_for_real = True

    def getAuthenticationURL(self, frob, perms):
        """See interfaces.IAPIAuth"""
        params = {'api_key': self.api_key, 'frob': frob,
                  'perms': ','.join(perms)}
        self.sign(params)
        url = 'http://www.flickr.com/services/auth/?%s'% \
              (urllib.urlencode(params))
        return url

    def authenticate(self, frob, perms, username, password):
        """See interfaces.IAPIAuth"""
        if not self._authenticate_for_real:
            return
        # Create a browser that will be used to log into the site.
        yahoo = browser.Browser(mech_browser=_InternalWebBrowser())
        yahoo.mech_browser.addheaders = [
            ("User-agent",
             "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)")]

        # Go to the login page.
        yahoo.open('http://www.flickr.com/signin')

        yahoo.mech_browser.deactivateRefreshHandler()
        yahoo.getLink('Sign in').click()

        # Now log in using the Yahoo! Sign In page.
        yahoo.getControl('Yahoo! ID').value = username
        yahoo.getControl('Password').value = password
        yahoo.mech_browser.activateRefreshHandler()
        yahoo.getControl('Sign In').click()

        if 'Invalid ID or password' in yahoo.contents:
            raise ValueError(
                'Username or password is incorrect. Sometimes the system '
                'also wants you to verify the user by asking for entering '
                'strings of an image, which is not supported here. Please '
                'log in at flickr.com once and retry again.')

        # Now allow the frob.
        yahoo.open(self.getAuthenticationURL(frob, perms))
        if 'Success!' not in yahoo.contents:
            yahoo.getControl("OK, I'LL ALLOW IT").click()


    def authenticateCookie(self, frob, perms, cookies):
        """See interfaces.IAPIAuth"""
        # Create a browser that will be used to log into the site.
        yahoo = browser.Browser(mech_browser=_InternalWebBrowser())
        yahoo.mech_browser.addheaders = [
            ("User-agent",
             "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)"),
            ("Cookie", cookies)
        ]
        # Now allow the frob.
        yahoo.open(self.getAuthenticationURL(frob, perms))
        if 'Success!' not in yahoo.contents:
            yahoo.getControl("OK, I'LL ALLOW IT").click()

    def getFrob(self):
        """See interfaces.IAPIAuth"""
        params = self.initParameters('flickr.auth.getFrob')
        self.sign(params)
        rsp = self.execute(params)
        return rsp.find('frob').text

    def checkToken(self, auth_token):
        """See interfaces.IAPIAuth"""
        params = self.initParameters(
            'flickr.auth.checkToken', auth_token=auth_token)
        rsp = self.execute(params)
        return Auth.fromElement(rsp.find('auth'))

    def getToken(self, frob):
        """See interfaces.IAPIAuth"""
        params = self.initParameters(
            'flickr.auth.getToken', frob=frob)
        self.sign(params)
        rsp = self.execute(params)
        return Auth.fromElement(rsp.find('auth'))

    def getFullToken(self, mini_token):
        """See interfaces.IAPIAuth"""
        # The API requires the mini-token to be 9 characters long after
        # optional dashes are removed.
        mini_token = mini_token.replace('-', '')
        assert len(mini_token) == 9

        params = self.initParameters(
            'flickr.auth.getFullToken', mini_token=mini_token)
        self.sign(params)
        rsp = self.execute(params)
        return Auth.fromElement(rsp.find('auth'))


def getFrob(api_key, secret):
    __doc__ = interfaces.IAPIAuth['getFrob'].__doc__
    return APIAuth(api_key, secret).getFrob()

def checkToken(api_key, auth_token):
    __doc__ = interfaces.IAPIAuth['checkToken'].__doc__
    return APIAuth(api_key).checkToken(auth_token)

def getToken(api_key, secret, frob):
    __doc__ = interfaces.IAPIAuth['checkToken'].__doc__
    return APIAuth(api_key, secret).getToken(frob)

def getFullToken(api_key, secret, mini_token):
    __doc__ = interfaces.IAPIAuth['getFullToken'].__doc__
    return APIAuth(api_key, secret).getFullToken(mini_token)

def getAuthenticationURL(api_key, secret, frob, perms):
    __doc__ = interfaces.IAPIAuth['getAuthenticationURL'].__doc__
    return APIAuth(api_key, secret).getAuthenticationURL(frob, perms)

def authenticate(api_key, frob, perms, username, password):
    __doc__ = interfaces.IAPIAuth['authenticate'].__doc__
    return APIAuth(api_key, secret).authenticate(
        frob, perms, username, password)

def authenticateCookie(api_key, frob, perms, cookies):
    __doc__ = interfaces.IAPIAuth['authenticateCookie'].__doc__
    return APIAuth(api_key, secret).authenticateCookie(
        frob, perms, cookies)
