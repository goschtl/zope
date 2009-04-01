##############################################################################
#
# Copyright (c) Zope Corporation and Contributors.
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

import base64
import ClientForm
import pprint
import simplejson
import StringIO
import urllib
import zc.ajax.session
import zope.app.exception.browser.unauthorized
import zope.app.security.interfaces
import zope.formlib.namedtemplate
import zope.interface
import zope.security.checker
import zope.security.interfaces
import zope.security.simplepolicies
import zope.testbrowser.testing

def _result(browser):
    # XXX TestBrowser needs a removeHeader
    browser.mech_browser.addheaders[:] = [
        header for header in browser.mech_browser.addheaders
        if header[0] != 'X-Requested-With']

    return simplejson.loads(browser.contents)

def call_form(browser, url, __params=(), __use_zope_type_decorators=True,
              **params):

    browser.addHeader('X-Requested-With', 'XMLHTTPRequest')
    if not (params or __params):
        browser.open(url)
        return _result(browser)

    
    params = params.copy()
    params.update(__params)

    pairs = []
    for n, v in params.items():
        if isinstance(v, list):
            if __use_zope_type_decorators:
                n += ':list'
            for vv in v:
                pairs.append((n, vv))
        else:
            pairs.append((n, v))

    multipart = False
    marshalled_pairs = []
    for n, v in pairs:
        if isinstance(v, str):
            v = v.encode('ascii')
        elif isinstance(v, bool):
            if __use_zope_type_decorators:
                n += ':boolean'
            v = v and '1' or ''
        elif isinstance(v, int):
            if __use_zope_type_decorators:
                n += ':int'
            v = str(v)
        elif isinstance(v, float):
            if __use_zope_type_decorators:
                n += ':float'
            v = str(v)
        elif isinstance(v, unicode):
            v = v.encode('utf-8')
        elif isinstance(v, tuple):
            multipart = True
        else:
            raise ValueError("can't marshal %r" % v)

        marshalled_pairs.append((n, v))

    if not multipart:
        browser.post(url,
                     '&'.join((n+'='+urllib.quote(v))
                              for (n, v)
                              in marshalled_pairs
                              )
                     )
        return _result(browser)

    body = StringIO.StringIO()
    headers = []
    mw = ClientForm.MimeWriter(body, headers)
    mw.startmultipartbody("form-data", add_to_http_hdrs=True, prefix=0)
    for n, v in marshalled_pairs:
        mw2 = mw.nextpart()
        if isinstance(v, tuple):
            filename, contenttype, data = v
            mw2.addheader("Content-disposition",
                          'form-data; name="%s"; filename="%s"'
                          % (n, filename))
            f = mw2.startbody(contenttype, prefix=0)
            f.write(data)
        else:
            mw2.addheader("Content-disposition", 'form-data; name="%s"' % n)
            f = mw2.startbody(prefix=0)
            f.write(v)

    mw.lastpart()
    body = body.getvalue()
    [[n, content_type]] = headers
    assert n.lower() == 'content-type'
    browser.post(url, body, content_type)
    return _result(browser)


def print_form(*a, **kw):
    pprint.pprint(call_form(*a, **kw), width=1)

class FormServer:

    def __init__(self, browser=None, zope_form_marshalling=False):
        if browser is None:
            browser = zope.testbrowser.testing.Browser()
        elif isinstance(browser, str):
            url = browser
            browser = zope.testbrowser.testing.Browser()
            browser.open(url)
            
        self.browser = browser
        self._zope_marshalling = zope_form_marshalling

    def __call__(self, method, __params=(), **params):
        return call_form(self.browser, method, __params,
                         __use_zope_type_decorators = self._zope_marshalling,
                         **params)

    def pprint(self, *a, **k):
        return pprint.pprint(self(*a, **k), width=1)

class Principal:

    description = ''

    def __init__(self, id):
        self.id = id
        self.title = 'principal: '+id

class UnauthenticatedPrincipal:

    id = 'unauthenticatedprincipal'
    title = u'UnauthenticatedPrincipal'
    description = u''

unauthenticatedPrincipal = UnauthenticatedPrincipal()

class Login:

    def __init__(self, context, request):
        pass

    def logout(self):
        """<html><body>
        Unauthorized! Add ?logged-in=name to log in. :)
        </body></html>
        """

class DumbAuth:

    zope.interface.implements(zope.app.security.interfaces.IAuthentication)

    def authenticate(self, request):
        if request.get('logout') is not None:
            return None

        if not 'login' in request:
            return None

        if 'login' in request.form:
            request.response.setCookie('login', '')

        return Principal('user')

    def unauthenticatedPrincipal(self):
        return unauthenticatedPrincipal

    def unauthorized(self, id, request):
        request.response.expireCookie('login')
        request.response.setStatus(401)
        return 

    def getPrincipal(self, id):
        return Principal(id)

unauth_template = zope.formlib.namedtemplate.NamedTemplateImplementation(
    lambda inst: """<html><body>
        Unauthorized! Add ?login to log in. :)
        </body></html>
        """,
    zc.ajax.session.Unauthorized)


class AuthenticatedAllowed(zope.security.simplepolicies.ParanoidSecurityPolicy):

    def checkPermission(self, permission, object):
        if permission is zope.security.checker.CheckerPublic:
            return True

        users = [p.principal
                 for p in self.participations
                 if p.principal is unauthenticatedPrincipal]

        return not users


    
