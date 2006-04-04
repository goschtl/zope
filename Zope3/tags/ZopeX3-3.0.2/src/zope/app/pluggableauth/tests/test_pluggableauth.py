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
"""Pluggable Auth Tests

$Id$
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.testing.doctestunit import DocTestSuite
from zope.interface.verify import verifyObject

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.site.tests import placefulsetup

from zope.exceptions import NotFoundError
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.app.tests import setup
from zope.exceptions import NotFoundError

from zope.app.pluggableauth import BTreePrincipalSource, \
     SimplePrincipal, PluggableAuthenticationService, \
     PrincipalAuthenticationView
from zope.app.pluggableauth.interfaces import IPrincipalSource

from zope.app.pluggableauth.interfaces import IUserSchemafied
from zope.app.security.interfaces import IPrincipal, ILoginPassword
from zope.app.security.basicauthadapter import BasicAuthAdapter

from zope.publisher.browser import TestRequest as Request

from zope.app.tests.placelesssetup import setUp, tearDown

import base64


class Setup(placefulsetup.PlacefulSetup, TestCase):

    def setUp(self):
        sm = placefulsetup.PlacefulSetup.setUp(self, site=True)
        ztapi.provideAdapter(IHTTPCredentials, ILoginPassword, BasicAuthAdapter)

        ztapi.browserView(IPrincipalSource, "login",
                          PrincipalAuthenticationView)

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
        self._one['slinkp'] = self._slinkp
        self._one['chrism'] = self._chrism
        self._two['slinkp2'] = self._slinkp2
        self._two['chrism2'] = self._chrism2

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
        id = self._slinkp.id
        self.assertEqual(self._slinkp, auth.getPrincipal(id))
        self.assertRaises(NotFoundError, self._fail_NoSourceId)
        self.assertRaises(NotFoundError, self._fail_BadIdType)
        self.assertRaises(NotFoundError, self._fail_BadIdLength)

    def testGetPrincipals(self):
        auth = self._auth
        self.failUnless(self._slinkp in auth.getPrincipals('slinkp'))
        self.failUnless(self._slinkp2 in auth.getPrincipals('slinkp'))

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
        self.assertEqual(p, one.getPrincipal(p.id))

class PrincipalAuthenticationViewTest(Setup):

    def test_authenticate(self):
        request = self.getRequest('chrism', '123')
        view = PrincipalAuthenticationView(self._one, request)
        self.assertEqual(self._chrism, view.authenticate())


def test_suite():
    t1 = makeSuite(AuthServiceTest)
    t2 = DocTestSuite('zope.app.pluggableauth',
                      setUp=setUp, tearDown=tearDown)
    t3 = makeSuite(BTreePrincipalSourceTest)
    t4 = makeSuite(PrincipalAuthenticationViewTest)
    return TestSuite((t1, t2, t3, t4))


if __name__=='__main__':
    main(defaultTest='test_suite')

