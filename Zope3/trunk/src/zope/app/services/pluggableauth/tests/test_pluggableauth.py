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
$Id: test_pluggableauth.py,v 1.4 2003/07/10 09:37:57 alga Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.auth import AuthenticationService
from zope.app.services.auth import User
from zope.app.services.servicenames import Adapters, Authentication
from zope.app.services.tests import placefulsetup

from zope.exceptions import NotFoundError
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.app.services.service import ServiceConfiguration
from zope.app.tests import setup
from zope.app.traversing import getPath, traverse
from zope.app.container.tests.test_icontainer import BaseTestIContainer
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.exceptions import NotFoundError

from zope.app.services.pluggableauth import BTreePrincipalSource, \
     SimplePrincipal, PluggableAuthenticationService, \
     PrincipalAuthenticationView, PrincipalWrapper

from zope.app.interfaces.services.pluggableauth import IUserSchemafied
from zope.app.interfaces.security import IPrincipal
from zope.interface.verify import verifyObject

from zope.publisher.browser import TestRequest as Request

import base64


class Setup(placefulsetup.PlacefulSetup, TestCase):

    def setUp(self):
        from zope.component.view import viewService
        from zope.app.interfaces.services.pluggableauth import IPrincipalSource
        sm = placefulsetup.PlacefulSetup.setUp(self, site=True)
        from zope.component import getService
        from zope.app.security.basicauthadapter import BasicAuthAdapter
        from zope.app.interfaces.security import ILoginPassword
        getService(None, Adapters).provideAdapter(
            IHTTPCredentials, ILoginPassword, BasicAuthAdapter)

        viewService.provideView(IPrincipalSource, "login",
                                IBrowserPresentation,
                                (PrincipalAuthenticationView,))

        auth = setup.addService(sm, "TestPluggableAuthenticationService",
                                 PluggableAuthenticationService())

        one = BTreePrincipalSource()
        two = BTreePrincipalSource()
        self._one = one
        self._two = two

        auth.addPrincipalSource('one', one)
        auth.addPrincipalSource('two', two)
        self._auth = auth
        self.createUsers()

    def createUsers(self):
        self._slinkp = SimplePrincipal('slinkp', '123')
        self._slinkp2 = SimplePrincipal('slinkp2', '123')
        self._chrism = SimplePrincipal('chrism', '123')
        self._chrism2 = SimplePrincipal('chrism2', '123')
        self._one.setObject('slinkp', self._slinkp)
        self._one.setObject('chrism', self._chrism)
        self._two.setObject('slinkp2', self._slinkp2)
        self._two.setObject('chrism2', self._chrism2)

    def getRequest(self, uid=None, passwd=None):
        if uid is None:
            return Request()
        if passwd is None:
            passwd = ''
        dict =  {
            'HTTP_AUTHORIZATION':
            "Basic %s" % base64.encodestring('%s:%s' % (uid, passwd))
         }
        return Request(**dict)


class AuthServiceTest(Setup):

    def testAuthServiceAuthenticate(self):
        auth = self._auth
        req = self.getRequest('slinkp', '123')
        pid = auth.authenticate(req).getLogin()
        self.assertEquals(pid, 'slinkp')
        req = self.getRequest('slinkp', 'hello2')
        p = auth.authenticate(req)
        self.assertEquals(p, None)
        req = self.getRequest('doesnotexit', 'hello')
        principal = auth.authenticate(req)
        self.assertEquals(principal, None)

    def testUnauthenticatedPrincipal(self):
        auth = self._auth
        self.assertEqual(None, auth.unauthenticatedPrincipal())

    def testUnauthorized(self):
        auth = self._auth
        req = self.getRequest('nobody', 'nopass')
        self.assertEqual(None, auth.unauthorized((None, None, None), req))

    def _fail_NoSourceId(self):
        self._auth.getPrincipal((self._auth.earmark, None, None))

    def _fail_BadIdType(self):
        self._auth.getPrincipal((self._auth.earmark, None, None))

    def _fail_BadIdLength(self):
        self._auth.getPrincipal((self._auth.earmark, None, None))

    def testAuthServiceGetPrincipal(self):
        auth = self._auth
        id = '\t'.join((auth.earmark, 'one', str(self._slinkp.getId())))
        self.assertEqual(self._slinkp, auth.getPrincipal(id))
        self.assertRaises(NotFoundError, self._fail_NoSourceId)
        self.assertRaises(NotFoundError, self._fail_BadIdType)
        self.assertRaises(NotFoundError, self._fail_BadIdLength)

    def testGetPrincipals(self):
        auth = self._auth
        self.failUnless(self._slinkp in auth.getPrincipals('slinkp'))
        self.failUnless(self._slinkp2 in auth.getPrincipals('slinkp'))


    def testPrincipalWrapper(self):
        wrapper = PrincipalWrapper(self._slinkp, self._auth, id='wrong')
        self.assertEqual(wrapper.getId(), 'wrong')


    def testPrincipalInterface(self):
        verifyObject(IUserSchemafied, self._slinkp)
        verifyObject(IPrincipal, self._slinkp)

class BTreePrincipalSourceTest(Setup):

    def test_authenticate(self):
        one = self._one
        self.assertEqual(None, one.authenticate('bogus', 'bogus'))
        self.assertEqual(self._slinkp, one.authenticate('slinkp', '123'))
        self.assertEqual(None, one.authenticate('slinkp', 'not really'))

    def test_getPrincipal(self):
        one = self._one
        p = self._slinkp
        self.assertEqual(p, one.getPrincipal(p.getId()))
        self.assertRaises(NotFoundError, one.getPrincipal, None)

class PrincipalAuthenticationViewTest(Setup):

    def test_authenticate(self):
        request = self.getRequest('chrism', '123')
        view = PrincipalAuthenticationView(self._one, request)
        self.assertEqual(self._chrism, view.authenticate())


def test_suite():
    t1 = makeSuite(AuthServiceTest)
    from zope.testing.doctestunit import DocTestSuite
    t2 = DocTestSuite('zope.app.services.pluggableauth')
    t3 = makeSuite(BTreePrincipalSourceTest)
    t4 = makeSuite(PrincipalAuthenticationViewTest)
    return TestSuite((t1, t2, t3, t4))


if __name__=='__main__':
    main(defaultTest='test_suite')

