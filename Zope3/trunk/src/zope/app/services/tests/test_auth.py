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
$Id: test_auth.py,v 1.9 2003/03/18 21:02:23 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.auth \
     import AuthenticationService, DuplicateLogin, DuplicateId
from zope.app.services.auth import User
from zope.app.interfaces.services.auth import IUser
from zope.app.services.servicenames import Adapters, Authentication

from zope.exceptions import NotFoundError
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.app.services.service import ServiceConfiguration
from zope.app.services.tests.eventsetup import EventSetup
from zope.app.traversing import getPhysicalPathString, traverse
from zope.app.interfaces.services.configuration import Active, Registered

from zope.app.container.tests.test_icontainer import BaseTestIContainer

class Request:

    __implements__ = IHTTPCredentials

    def __init__(self, lpw):
        self.__lpw = lpw

    def _authUserPW(self):
        return self.__lpw

    challenge = None
    def unauthorized(self, challenge):
        self.challenge = challenge


class AuthSetup(EventSetup):

    def setUp(self):
        EventSetup.setUp(self)

        from zope.component import getService
        from zope.app.security.basicauthadapter import BasicAuthAdapter
        from zope.app.interfaces.security import ILoginPassword
        getService(None, Adapters).provideAdapter(
            IHTTPCredentials, ILoginPassword, BasicAuthAdapter)

        folder = self.rootFolder

        if not folder.hasServiceManager():
            self.createServiceManager(folder)

        default = traverse(folder, '++etc++Services/default')
        key = default.setObject("AuthenticationService", AuthenticationService())
        auth = traverse(default, key)

        path = getPhysicalPathString(auth)
        configuration = ServiceConfiguration(Authentication, path)
        configure = traverse(default, 'configure')
        key = configure.setObject(None, configuration)
        traverse(configure, key).status = Active

        auth.setObject('srichter', User('srichter', 'Stephan', 'Richter',
                                        'srichter', 'hello'))
        auth.setObject('jim', User('jim', 'Jim', 'Fulton',
                                   'jim', 'hello2'))
        auth.setObject('stevea', User('stevea', 'Steve', 'Alexander',
                                      'stevea', 'hello3'))

        self._auth = auth

    def createStandardServices(self):
        EventSetup.createStandardServices(self)

        from zope.component import getServiceManager
        from zope.app.security.registries.principalregistry \
             import principalRegistry
        from zope.app.interfaces.security import IAuthenticationService
        sm = getServiceManager(None)
        sm.defineService(Authentication, IAuthenticationService)
        sm.provideService(Authentication, principalRegistry)


class AuthServiceTest(AuthSetup, TestCase):

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
        self.assertRaises(NotFoundError, auth.getPrincipal, 'srichter2')

    def testGetPrincipals(self):
        auth = self._auth
        self.assertEqual([auth['srichter']], auth.getPrincipals('srichter'))


class TestAuthAsIContainer(BaseTestIContainer, TestCase):

    def makeTestObject(self):
        return AuthenticationService()

    def makeTestData(self):
        return [ (k, User(k, k+'title', k+'desc', k, k+'pass'))
                    for k in 'abcdefghijkl' ]


def test_suite():
    t1 = makeSuite(AuthServiceTest)
    t2 = makeSuite(TestAuthAsIContainer)
    return TestSuite((t1, t2))

if __name__=='__main__':
    main(defaultTest='test_suite')
