# -*- coding: latin-1 -*-
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
"""HTTP Publisher Tests

$Id: test_http.py,v 1.27 2004/03/18 20:03:56 srichter Exp $
"""
import unittest

# XXX evil zope.app imports :(
from zope.app.site.tests.placefulsetup import PlacefulSetup
from zope.app.security.interfaces import IPrincipal

# XX, Hm, zope.component dependency is suspect
import zope.component

from zope.interface import implements
from zope.publisher.interfaces.logginginfo import ILoggingInfo
from zope.publisher.http import HTTPRequest
from zope.publisher.publish import publish
from zope.publisher.base import DefaultPublication
from zope.publisher.interfaces.http import IHTTPRequest

from zope.i18n.interfaces.locales import ILocale

from zope.interface.verify import verifyObject

from StringIO import StringIO


class UserStub:
    implements(IPrincipal)
    def __init__(self, id):
        self._id = id
    def getId(self):
        return self._id

class PrincipalLoggingStub:
    implements(ILoggingInfo)

    def __init__(self, object):
        self.object = object

    def getLogMessage(self):
        return self.object.getId()


class HTTPTests(PlacefulSetup, unittest.TestCase):

    _testEnv =  {
        'PATH_INFO':          '/folder/item',
        'a':                  '5',
        'b':                  6,
        'SERVER_URL':         'http://foobar.com',
        'HTTP_HOST':          'foobar.com',
        'CONTENT_LENGTH':     '0',
        'HTTP_AUTHORIZATION': 'Should be in accessible',
        'GATEWAY_INTERFACE':  'TestFooInterface/1.0',
        'HTTP_OFF_THE_WALL':  "Spam 'n eggs",
        'HTTP_ACCEPT_CHARSET': 'ISO-8859-1, UTF-8;q=0.66, UTF-16;q=0.33',
    }

    def setUp(self):
        PlacefulSetup.setUp(self)
        class AppRoot:
            " "

        class Folder:
            " "

        class Item:
            " "
            def __call__(self, a, b):
                return "%s, %s" % (`a`, `b`)

        self.app = AppRoot()
        self.app.folder = Folder()
        self.app.folder.item = Item()
        self.app.xxx = Item()

    def _createRequest(self, extra_env={}, body="", outstream=None):
        env = self._testEnv.copy()
        env.update(extra_env)
        if len(body):
            env['CONTENT_LENGTH'] = str(len(body))

        publication = DefaultPublication(self.app)
        if outstream is None:
            outstream = StringIO()
        instream = StringIO(body)
        request = HTTPRequest(instream, outstream, env)
        request.setPublication(publication)
        return request

    def _publisherResults(self, extra_env={}, body=""):
        outstream = StringIO()
        request = self._createRequest(extra_env, body, outstream=outstream)
        publish(request, handle_errors=0)
        return outstream.getvalue()

    def testTraversalToItem(self):
        res = self._publisherResults()
        self.failUnlessEqual(
            res,
            "Status: 200 Ok\r\n"
            "Content-Length: 6\r\n"
            "X-Powered-By: Zope (www.zope.org), Python (www.python.org)\r\n"
            "\r\n"
            "'5', 6")

    def testRequestEnvironment(self):
        req = self._createRequest()
        publish(req, handle_errors=0) # Force expansion of URL variables

        self.assertEquals(str(req.URL), 'http://foobar.com/folder/item')
        self.assertEquals(req.URL['-1'], 'http://foobar.com/folder')
        self.assertEquals(req.URL['-2'], 'http://foobar.com')
        self.assertRaises(KeyError, req.URL.__getitem__, '-3')

        self.assertEquals(req.URL['0'], 'http://foobar.com')
        self.assertEquals(req.URL['1'], 'http://foobar.com/folder')
        self.assertEquals(req.URL['2'], 'http://foobar.com/folder/item')
        self.assertRaises(KeyError, req.URL.__getitem__, '3')

        self.assertEquals(req['SERVER_URL'], 'http://foobar.com')
        self.assertEquals(req['HTTP_HOST'], 'foobar.com')
        self.assertEquals(req['PATH_INFO'], '/folder/item')
        self.assertEquals(req['CONTENT_LENGTH'], '0')
        self.assertRaises(KeyError, req.__getitem__, 'HTTP_AUTHORIZATION')
        self.assertEquals(req['GATEWAY_INTERFACE'], 'TestFooInterface/1.0')
        self.assertEquals(req['HTTP_OFF_THE_WALL'], "Spam 'n eggs")

        self.assertRaises(KeyError, req.__getitem__,
                          'HTTP_WE_DID_NOT_PROVIDE_THIS')

    def testRequestLocale(self):
        eq = self.assertEqual
        unless = self.failUnless
        for httplang in ('it', 'it-ch', 'it-CH', 'IT', 'IT-CH', 'IT-ch'):
            req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': httplang})
            locale = req.locale
            unless(ILocale.providedBy(locale))
            parts = httplang.split('-')
            lang = parts.pop(0).lower()
            territory = variant = None
            if parts:
                territory = parts.pop(0).upper()
            if parts:
                variant = parts.pop(0).upper()
            eq(locale.id.language, lang)
            eq(locale.id.territory, territory)
            eq(locale.id.variant, variant)
        # Now test for non-existant locale fallback
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'xx'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, None)
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

        # If the first language is not available we should try others
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'xx,en;q=0.5'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, 'en')
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

        # Regression test: there was a bug where territory and variant were
        # not reset
        req = self._createRequest({'HTTP_ACCEPT_LANGUAGE': 'xx-YY,en;q=0.5'})
        locale = req.locale
        unless(ILocale.providedBy(locale))
        eq(locale.id.language, 'en')
        eq(locale.id.territory, None)
        eq(locale.id.variant, None)

    def testCookies(self):
        cookies = {
            'HTTP_COOKIE': 'foo=bar; spam="eggs", this="Should be accepted"'
        }
        req = self._createRequest(extra_env=cookies)

        self.assertEquals(req.cookies[u'foo'], u'bar')
        self.assertEquals(req[u'foo'], u'bar')

        self.assertEquals(req.cookies[u'spam'], u'eggs')
        self.assertEquals(req[u'spam'], u'eggs')

        self.assertEquals(req.cookies[u'this'], u'Should be accepted')
        self.assertEquals(req[u'this'], u'Should be accepted')

    def testHeaders(self):
        headers = {
            'TEST_HEADER': 'test',
            'Another-Test': 'another',
        }
        req = self._createRequest(extra_env=headers)
        self.assertEquals(req.headers[u'TEST_HEADER'], u'test')
        self.assertEquals(req.headers[u'TEST-HEADER'], u'test')
        self.assertEquals(req.headers[u'test_header'], u'test')
        self.assertEquals(req.getHeader('TEST_HEADER', literal=True), u'test')
        self.assertEquals(req.getHeader('TEST-HEADER', literal=True), None)
        self.assertEquals(req.getHeader('test_header', literal=True), None)
        self.assertEquals(req.getHeader('Another-Test', literal=True), 'another')

    def testBasicAuth(self):
        from zope.publisher.interfaces.http import IHTTPCredentials
        import base64
        req = self._createRequest()
        verifyObject(IHTTPCredentials, req)
        lpq = req._authUserPW()
        self.assertEquals(lpq, None)
        env = {}
        login, password = ("tim", "123")
        s = base64.encodestring("%s:%s" % (login, password)).rstrip()
        env['HTTP_AUTHORIZATION'] = "Basic %s" % s
        req = self._createRequest(env)
        lpw = req._authUserPW()
        self.assertEquals(lpw, (login, password))

    def testSetUser(self):
        class HTTPTaskStub:
            auth_user_name = None
            def setAuthUserName(self, name):
                self.auth_user_name = name

        as = zope.component.getService(None, 'Adapters')
        as.register([IPrincipal], ILoggingInfo, '', PrincipalLoggingStub)
        task = HTTPTaskStub()
        req = self._createRequest(outstream=task)
        req.setUser(UserStub("jim"))
        self.assert_(not req.response._outstream.auth_user_name)
        req = self._createRequest(outstream=task)
        req.response.setHTTPTransaction(task)
        req.setUser(UserStub("jim"))
        self.assertEquals(req.response.http_transaction.auth_user_name, "jim")

    def testIPresentationRequest(self):
        # test the IView request
        r = self._createRequest()

        self.assertEqual(r.getPresentationSkin(), '')
        r.setPresentationSkin('morefoo')
        self.assertEqual(r.getPresentationSkin(), 'morefoo')

    def test_method(self):
        r = self._createRequest(extra_env={'REQUEST_METHOD':'SPAM'})
        self.assertEqual(r.method, 'SPAM')
        r = self._createRequest(extra_env={'REQUEST_METHOD':'eggs'})
        self.assertEqual(r.method, 'EGGS')

    def test_setApplicationServer(self):
        req = self._createRequest()
        req.setApplicationServer('foo')
        self.assertEquals(req._app_server, 'http://foo')
        req.setApplicationServer('foo', proto='https')
        self.assertEquals(req._app_server, 'https://foo')
        req.setApplicationServer('foo', proto='https', port=8080)
        self.assertEquals(req._app_server, 'https://foo:8080')
        req.setApplicationServer('foo', proto='http', port='9673')
        self.assertEquals(req._app_server, 'http://foo:9673')
        req.setApplicationServer('foo', proto='https', port=443)
        self.assertEquals(req._app_server, 'https://foo')
        req.setApplicationServer('foo', proto='https', port='443')
        self.assertEquals(req._app_server, 'https://foo')
        req.setApplicationServer('foo', port=80)
        self.assertEquals(req._app_server, 'http://foo')
        req.setApplicationServer('foo', proto='telnet', port=80)
        self.assertEquals(req._app_server, 'telnet://foo:80')

    def test_setApplicationNames(self):
        req = self._createRequest()
        names = ['x', 'y', 'z']
        req.setVirtualHostRoot(names)
        self.assertEquals(req._app_names, ['x', 'y', 'z'])
        names[0] = 'muahahahaha'
        self.assertEquals(req._app_names, ['x', 'y', 'z'])

    def test_setVirtualHostRoot(self):
        req = self._createRequest()
        req._traversed_names = ['x', 'y']
        req._last_obj_traversed = object()
        req.setVirtualHostRoot()
        self.failIf(req._traversed_names)
        self.assertEquals(req._vh_root, req._last_obj_traversed)

    def test_getVirtualHostRoot(self):
        req = self._createRequest()
        self.assertEquals(req.getVirtualHostRoot(), None)
        req._vh_root = object()
        self.assertEquals(req.getVirtualHostRoot(), req._vh_root)

    def test_traverse(self):
        req = self._createRequest()
        req.traverse(self.app)
        self.assertEquals(req._traversed_names, ['folder', 'item'])

        # setting it during traversal matters
        req = self._createRequest()
        def hook(self, object, req=req, app=self.app):
            if object is app.folder:
                req.setVirtualHostRoot()
        req.publication.callTraversalHooks = hook
        req.traverse(self.app)
        self.assertEquals(req._traversed_names, ['item'])
        self.assertEquals(req._vh_root, self.app.folder)

    def testInterface(self):
        from zope.publisher.interfaces.http import IHTTPCredentials
        from zope.publisher.interfaces.http import IHTTPApplicationRequest
        rq = self._createRequest()
        verifyObject(IHTTPRequest, rq)
        verifyObject(IHTTPCredentials, rq)
        verifyObject(IHTTPApplicationRequest, rq)

    def testDeduceServerURL(self):
        req = self._createRequest()
        deduceServerURL = req._HTTPRequest__deduceServerURL
        req._environ = {'HTTP_HOST': 'example.com:80'}
        self.assertEquals(deduceServerURL(), 'http://example.com')
        req._environ = {'HTTP_HOST': 'example.com:8080'}
        self.assertEquals(deduceServerURL(), 'http://example.com:8080')
        req._environ = {'HTTP_HOST': 'example.com:443', 'HTTPS': 'on'}
        self.assertEquals(deduceServerURL(), 'https://example.com')
        req._environ = {'HTTP_HOST': 'example.com:80', 'HTTPS': 'ON'}
        self.assertEquals(deduceServerURL(), 'https://example.com:80')
        req._environ = {'HTTP_HOST': 'example.com:8080',
                        'SERVER_PORT_SECURE': '1'}
        self.assertEquals(deduceServerURL(), 'https://example.com:8080')
        req._environ = {'SERVER_NAME': 'example.com', 'SERVER_PORT':'8080',
                        'SERVER_PORT_SECURE': '0'}
        self.assertEquals(deduceServerURL(), 'http://example.com:8080')
        req._environ = {'SERVER_NAME': 'example.com'}
        self.assertEquals(deduceServerURL(), 'http://example.com')

    def testUnicodeURLs(self):
        req = self._createRequest(
            {'PATH_INFO': '/%C3%A4%C3%B6/%C3%BC%C3%9F/foo/bar.html'})
        self.assertEqual(req._traversal_stack,
                         [u'bar.html', u'foo', u'��', u'��'])


class ConcreteHTTPTests(HTTPTests):
    """Tests that we don't have to worry about subclasses inheriting and
    breaking.
    """

    def test_shiftNameToApplication(self):
        r = self._createRequest()
        publish(r, handle_errors=0)
        appurl = r.getApplicationURL()

        # Verify that we can shift. It would be a little more realistic
        # if we could test this during traversal, but the api doesn't
        # let us do that.
        r = self._createRequest(extra_env={"PATH_INFO": "/xxx"})
        publish(r, handle_errors=0)
        r.shiftNameToApplication()
        self.assertEquals(r.getApplicationURL(), appurl+"/xxx")
        
        # Verify that we can only shift if we've traversed only a single name
        r = self._createRequest(extra_env={"PATH_INFO": "/folder/item"})
        publish(r, handle_errors=0)
        self.assertRaises(ValueError, r.shiftNameToApplication)



class TestHTTPResponse(unittest.TestCase):

    def testInterface(self):
        from zope.publisher.http import HTTPResponse
        from zope.publisher.interfaces.http import IHTTPResponse
        from zope.publisher.interfaces.http import IHTTPApplicationResponse
        from zope.publisher.interfaces import IResponse
        rp = HTTPResponse(StringIO())
        verifyObject(IHTTPResponse, rp)
        verifyObject(IHTTPApplicationResponse, rp)
        verifyObject(IResponse, rp)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConcreteHTTPTests))
    suite.addTest(unittest.makeSuite(TestHTTPResponse))
    return suite


if __name__ == '__main__':
    unittest.main()
