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
"""

Revision information:
$Id: test_unauthorized.py,v 1.1 2003/02/05 11:34:55 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.publisher.base import TestRequest
from zope.proxy.context import ContextWrapper
from zope.app.interfaces.security import IAuthenticationService, IPrincipal

class DummyPrincipal:
    __implements__ = IPrincipal  # this is a lie

    def __init__(self, id):
        self.id = id

    def getId(self):
        return self.id

class DummyAuthService:
    __implements__ = IAuthenticationService  # this is a lie

    def unauthorized(self, principal_id, request):
        self.principal_id = principal_id
        self.request = request

class Test(TestCase):

    def test(self):
        from zope.app.browser.exception.unauthorized import Unauthorized
        exception = Exception()
        try:
            raise exception
        except:
            pass
        request = TestRequest('/')
        authservice = DummyAuthService()
        request.user = ContextWrapper(DummyPrincipal(23), authservice)
        u = Unauthorized(exception, request)
        u.issueChallenge()
        self.failUnless(authservice.request is request)
        self.assertEqual(authservice.principal_id, 23)
        self.assertEqual(' '.join(u.traceback.split()),
            '<p>Traceback (innermost last): '
            '<ul> '
            '<li> Module zope.app.browser.exception.tests.test_unauthorized, '
            'line 47, in test</li> '
            '</ul>Exception '
            '</p>'
            )

def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
