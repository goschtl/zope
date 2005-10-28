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
"""Test Unauthorized Exception Views

$Id$
"""
from unittest import TestCase, main, makeSuite
from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.app.security.interfaces import IAuthenticationService, IPrincipal
from zope.app.container.contained import contained
from zope.app.exception.browser.unauthorized import Unauthorized
from zope.app.event.tests.placelesssetup import PlacelessSetup

class Unauthorized(Unauthorized):
    """Unusually done by ZCML."""

    def __init__(self, context, request):
        self.context = context
        self.request = request


class DummyPrincipal(object):
    implements(IPrincipal)  # this is a lie

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

class DummyAuthService(object):
    implements(IAuthenticationService)  # this is a lie

    def unauthorized(self, principal_id, request):
        self.principal_id = principal_id
        self.request = request

class DummyPrincipalSource(object):
    pass

class Test(TestCase, PlacelessSetup):

    def test(self):
        exception = Exception()
        try:
            raise exception
        except:
            pass
        request = TestRequest('/')
        authservice = DummyAuthService()
        request.setPrincipal(contained(DummyPrincipal(23), authservice))
        u = Unauthorized(exception, request)
        u.issueChallenge()

        # Make sure the response status was set
        self.assertEqual(request.response.getStatus(), 403)

        # Make sure the auth service was called
        self.failUnless(authservice.request is request)
        self.assertEqual(authservice.principal_id, 23)

    def testPluggableAuthService(self):
        exception = Exception()
        try:
            raise exception
        except:
            pass
        request = TestRequest('/')
        authservice = DummyAuthService()
        psrc = DummyPrincipalSource()
        psrc = contained(psrc, authservice)
        request.setPrincipal(contained(DummyPrincipal(23), psrc))
        u = Unauthorized(exception, request)
        u.issueChallenge()

        # Make sure the response status was set
        self.assertEqual(request.response.getStatus(), 403)

        # Make sure the auth service was called
        self.failUnless(authservice.request is request)
        self.assertEqual(authservice.principal_id, 23)

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
