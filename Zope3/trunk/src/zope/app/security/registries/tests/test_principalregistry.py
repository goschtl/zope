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
import unittest

from zope.app.security.registries.principalregistry import PrincipalRegistry
from zope.app.security.registries.principalregistry \
     import DuplicateLogin, DuplicateId
from zope.exceptions import NotFoundError
from zope.publisher.interfaces.http import IHTTPCredentials
from zope.app.services.tests.placefulsetup \
           import PlacefulSetup
from zope.app.services.servicenames import Adapters

class Request:

    __implements__ = IHTTPCredentials

    def __init__(self, lpw):
        self.__lpw = lpw

    def _authUserPW(self):
        return self.__lpw

    challenge = None
    def unauthorized(self, challenge):
        self.challenge = challenge


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)

        from zope.component import getService
        from zope.app.security.basicauthadapter import BasicAuthAdapter
        from zope.app.interfaces.security import ILoginPassword
        getService(None,Adapters).provideAdapter(
            IHTTPCredentials, ILoginPassword, BasicAuthAdapter)

        self.reg = PrincipalRegistry()

        self.reg.definePrincipal('1', 'Tim Peters', 'Sir Tim Peters',
                                 'tim', '123')
        self.reg.definePrincipal('2', 'Jim Fulton', 'Sir Jim Fulton',
                                 'jim', '456')

    def testRegistered(self):
        p = self.reg.getPrincipal('1')
        self.assertEqual(p.getId(), '1')
        self.assertEqual(p.getTitle(), 'Tim Peters')
        self.assertEqual(p.getDescription(), 'Sir Tim Peters')
        self.assertEqual(p.getRoles(), ())
        p = self.reg.getPrincipal('2')
        self.assertEqual(p.getId(), '2')
        self.assertEqual(p.getTitle(), 'Jim Fulton')
        self.assertEqual(p.getDescription(), 'Sir Jim Fulton')
        self.assertEqual(p.getRoles(), ())

        self.assertEqual(len(self.reg.getPrincipals('')), 2)

    def testUnRegistered(self):
        self.assertRaises(NotFoundError, self.reg.getPrincipal, '3')

    def testDup(self):
        self.assertRaises(DuplicateId,
                          self.reg.definePrincipal,
                          '1', 'Tim Peters', 'Sir Tim Peters',
                          'tim2', '123')
        self.assertRaises(DuplicateLogin,
                          self.reg.definePrincipal,
                          '3', 'Tim Peters', 'Sir Tim Peters',
                          'tim', '123')
        self.assertRaises(NotFoundError, self.reg.getPrincipal, '3')
        self.assertEqual(len(self.reg.getPrincipals('')), 2)

    def testSearch(self):
        r = self.reg.getPrincipals('J')
        self.assertEquals(len(r), 1)
        self.failUnless(r[0] is self.reg.getPrincipal('2'))

    def testByLogin(self):
        tim = self.reg.getPrincipalByLogin('tim')
        self.assertEquals(tim.getLogin(), 'tim')
        jim = self.reg.getPrincipalByLogin('jim')
        self.assertEquals(jim.getLogin(), 'jim')
        self.assertRaises(NotFoundError,
                          self.reg.getPrincipalByLogin, 'kim')

    def testValidation(self):
        tim = self.reg.getPrincipalByLogin('tim')
        self.assert_(tim.validate('123'))
        self.failIf(tim.validate('456'))
        self.failIf(tim.validate(''))
        self.failIf(tim.validate('1234'))
        self.failIf(tim.validate('12'))

    def testAuthenticate(self):
        req = Request(('tim', '123'))
        pid = self.reg.authenticate(req).getId()
        self.assertEquals(pid, '1')
        req = Request(('tim', '1234'))
        p = self.reg.authenticate(req)
        self.assertEquals(p, None)
        req = Request(('kim', '123'))
        p = self.reg.authenticate(req)
        self.assertEquals(p, None)

    def testUnauthorized(self):
        request = Request(None)
        self.reg.unauthorized(self.reg.unauthenticatedPrincipal(), request)
        self.assertEquals(request.challenge, "basic realm=zope")
        request = Request(None)
        self.reg.unauthorized(None, request)
        self.assertEquals(request.challenge, "basic realm=zope")
        request = Request(None)
        self.reg.unauthorized("1", request)
        self.assertEquals(request.challenge, None)

    def testDefaultPrincipal(self):
        self.assertEquals(self.reg.unauthenticatedPrincipal(), None)
        self.assertRaises(DuplicateId, self.reg.defineDefaultPrincipal,
                          "1", "tim")
        self.reg.defineDefaultPrincipal("everybody", "Default Principal")
        self.assertEquals(self.reg.unauthenticatedPrincipal().getId(), "everybody")
        self.reg.defineDefaultPrincipal("anybody", "Default Principal",
                                        "This is the default headmaster")
        self.assertEquals(self.reg.unauthenticatedPrincipal().getId(), "anybody")
        self.assertRaises(NotFoundError, self.reg.getPrincipal, "everybody")
        p = self.reg.getPrincipal("anybody")
        self.assertEquals(p.getId(), "anybody")
        self.assertEquals(p.getTitle(), "Default Principal")
        self.assertEquals(p.getRoles(), ())
        self.assertRaises(DuplicateId, self.reg.definePrincipal,
                          "anybody", "title")

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
