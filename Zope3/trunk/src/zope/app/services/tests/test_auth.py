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
$Id: test_auth.py,v 1.2 2002/12/25 14:13:20 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.auth \
     import AuthenticationService, DuplicateLogin, DuplicateId
from zope.app.services.auth import User
from zope.app.interfaces.services.auth import IUser

from zope.exceptions import NotFoundError
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.app.services.tests.placefulsetup \
           import PlacefulSetup

class Request:

    __implements__ = IHTTPCredentials

    def __init__(self, lpw):
        self.__lpw = lpw

    def _authUserPW(self):
        return self.__lpw

    challenge = None
    def unauthorized(self, challenge):
        self.challenge = challenge


class AuthServiceTest(TestCase, PlacefulSetup):

    def setUp(self):
        PlacefulSetup.setUp(self)

        from zope.component import getService
        from zope.app.security.basicauthadapter import BasicAuthAdapter
        from zope.app.interfaces.security import ILoginPassword
        getService(None, "Adapters").provideAdapter(
            IHTTPCredentials, ILoginPassword, BasicAuthAdapter)

        auth = AuthenticationService()
        auth.setObject('srichter', User('srichter', 'Stephan', 'Richter',
                                        'srichter', 'hello'))
        auth.setObject('jim', User('jim', 'Jim', 'Foulton',
                                        'jim', 'hello2'))
        auth.setObject('stevea', User('stevea', 'Steve', 'Alexander',
                                        'stevea', 'hello3'))
        self._auth = auth


    def testGetPrincipalByLogin(self):
        auth = self._auth
        self.assertEqual(auth['srichter'],
                         auth.getPrincipalByLogin('srichter'))

    def testAuthenticate(self):
        auth = self._auth
        req = Request(('srichter', 'hello'))
        pid = auth.authenticate(req).getId()
        self.assertEquals(pid, 'srichter')
        req = Request(('srichter', 'hello2'))
        p = auth.authenticate(req)
        self.assertEquals(p, None)
        req = Request(('doesnotexit', 'hello'))
        principal = auth.authenticate(req)
        self.assertEquals(principal, None)

    def testUnauthenticatedPrincipal(self):
        auth = self._auth
        self.assertEqual(None, auth.unauthenticatedPrincipal())

    def testUnauthorized(self):
        auth = self._auth
        request = Request(None)
        auth.unauthorized(auth.unauthenticatedPrincipal(), request)
        self.assertEquals(request.challenge, "basic realm=zope")
        request = Request(None)
        auth.unauthorized(None, request)
        self.assertEquals(request.challenge, "basic realm=zope")
        request = Request(None)
        auth.unauthorized("srichter", request)
        self.assertEquals(request.challenge, None)

    def testGetPrincipal(self):
        auth = self._auth
        self.assertEqual(auth['srichter'], auth.getPrincipal('srichter'))
        self.assertEqual(None, auth.getPrincipal('srichter2'))

    def testGetPrincipals(self):
        auth = self._auth
        self.assertEqual([auth['srichter']], auth.getPrincipals('srichter'))

def test_suite():
    return makeSuite(AuthServiceTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
