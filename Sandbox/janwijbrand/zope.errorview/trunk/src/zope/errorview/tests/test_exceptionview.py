##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Unauthorized Exception Test

$Id: test_unauthorized.py 119650 2011-01-18 14:58:35Z janwijbrand $
"""
from unittest import TestCase
from zope.errorview.unauthorized import Unauthorized
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.http import IHTTPException
from zope.publisher.interfaces.http import MethodNotAllowed
from zope.security.interfaces import Unauthorized
from zope.publisher.interfaces import TraversalException
from zope.errorview import http
from zope.browser.interfaces import ISystemErrorView

class TestErrorViews(TestCase):

    def setUp(self):
        self.request = TestRequest()

    def test_exceptionviewbase(self):
        view = http.ExceptionViewBase(Exception(), self.request)
        self.failUnless(IHTTPException.providedBy(view))
        # Render the view.
        self.assertEquals(str(view), '')
        self.assertEquals(view(), '')
        self.assertEqual(self.request.response.getStatus(), 500)

    def test_exceptionview(self):
        view = http.ExceptionView(Exception(), self.request)
        self.failUnless(IHTTPException.providedBy(view))
        self.failUnless(ISystemErrorView.providedBy(view))
        self.assertTrue(view.isSystemError())
        # Render the view.
        self.assertEquals(str(view), '')
        self.assertEquals(view(), '')
        self.assertEqual(self.request.response.getStatus(), 500)

    def test_traversalexceptionview(self):
        view = http.TraversalExceptionView(TraversalException(), self.request)
        self.failUnless(IHTTPException.providedBy(view))
        # Render the view.
        self.assertEquals(str(view), '')
        self.assertEquals(view(), '')
        self.assertEqual(self.request.response.getStatus(), 404)
        # XXX test the MKCOL verb here too.

    def test_unauthorizedexceptionview(self):
        view = http.UnauthorizedView(Unauthorized(), self.request)
        self.failUnless(IHTTPException.providedBy(view))
        # Render the view.
        self.assertEquals(str(view), '')
        self.assertEquals(view(), '')
        self.assertEqual(self.request.response.getStatus(), 401)
        self.failUnless(
            self.request.response.getHeader(
                'WWW-Authenticate', '', True).startswith('basic'))

    def test_methodnotallowedview(self):
        error = MethodNotAllowed(object(), self.request)
        view = http.MethodNotAllowedView(error, self.request)
        self.failUnless(IHTTPException.providedBy(view))
        # Render the view.
        self.assertEquals(str(view), '')
        self.assertEquals(view(), '')
        self.assertEquals(self.request.response.getStatus(), 405)
        self.assertEquals(self.request.response.getHeader('Allow'), '')

        class MyMethodNotAllowedView(http.MethodNotAllowedView):
            def allowed(self):
                return 'GET', 'POST', 'PUT', 'DELETE'

        MyMethodNotAllowedView(error, self.request)()
        self.assertEquals(self.request.response.getStatus(), 405)
        self.assertEquals(
            self.request.response.getHeader('Allow'), 'GET, POST, PUT, DELETE')






