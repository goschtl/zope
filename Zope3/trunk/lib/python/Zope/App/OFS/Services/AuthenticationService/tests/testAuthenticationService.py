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
$Id: testAuthenticationService.py,v 1.3 2002/12/06 13:12:08 itamar Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.OFS.Services.AuthenticationService.AuthenticationService \
     import AuthenticationService, DuplicateLogin, DuplicateId
from Zope.App.OFS.Services.AuthenticationService.User import User
from Zope.App.OFS.Services.AuthenticationService.IUser import IUser

from Zope.Exceptions import NotFoundError
from Zope.Publisher.HTTP.IHTTPCredentials import IHTTPCredentials
from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup \
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

        from Zope.ComponentArchitecture import getService
        from Zope.App.Security.BasicAuthAdapter import BasicAuthAdapter
        from Zope.App.Security.ILoginPassword import ILoginPassword
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

    def testIsAddable(self):
        auth = self._auth
        self.assertEqual(1, auth.isAddable(IUser))
        self.assertEqual(0, auth.isAddable(IHTTPCredentials))


def test_suite():
    return makeSuite(AuthServiceTest)

if __name__=='__main__':
    main(defaultTest='test_suite')
