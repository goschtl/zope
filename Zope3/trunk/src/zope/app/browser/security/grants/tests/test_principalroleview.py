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

$Id: test_principalroleview.py,v 1.6 2003/03/03 23:16:04 gvanrossum Exp $
"""

import unittest

from zope.app.services.tests.placefulsetup\
           import PlacefulSetup
from zope.component import getServiceManager
from zope.app.services.servicenames import Roles, Authentication

from zope.app.interfaces.security import IRoleService
from zope.app.interfaces.security import IAuthenticationService

from zope.app.interfaces.security import IPrincipalRoleManager
from zope.app.interfaces.security import IPrincipalRoleMap
from zope.publisher.browser import TestRequest
from zope.app.interfaces.services.interfaces import ISimpleService

class DummySetting:
    def __init__(self, name):
        self._name = name
    def getName(self):
        return self._name

class DummyManager:

    __implements__ = IPrincipalRoleManager

    def getSetting(self, role, principal):
        return DummySetting('%r:%r' % (role, principal))

class DummyRoleService:

    __implements__ = IRoleService, ISimpleService

    def __init__(self, roles):
        self._roles = roles

    def getRoles(self):
        return self._roles

class DummyObject:
    def __init__(self, id, title):
        self._id = id
        self._title = title

    def getId(self):
        return self._id

    def getTitle(self):
        return self._title

class DummyAuthenticationService:

    __implements__ = IAuthenticationService, ISimpleService

    def __init__(self, principals):
        self._principals = principals

    def getPrincipals(self, name):
        return self._principals

class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self._roles = []
        self._roles.append(DummyObject('qux', 'Qux'))
        self._roles.append(DummyObject('baz', 'Baz'))
        defineService=getServiceManager(None).defineService
        provideService=getServiceManager(None).provideService

        defineService(Roles, IRoleService)
        provideService(Roles
                      , DummyRoleService(roles = self._roles))

        defineService(Authentication, IAuthenticationService)

        self._principals = []
        self._principals.append(DummyObject('foo', 'Foo'))
        self._principals.append(DummyObject('bar', 'Bar'))

        provideService(Authentication,
            DummyAuthenticationService(principals = self._principals))

    def _makeOne(self):
        from zope.app.browser.security.grants.principalroleview \
             import PrincipalRoleView
        return PrincipalRoleView(DummyManager(), TestRequest())

    def testRoles(self):
        view = self._makeOne()
        roles = list(view.getAllRoles())
        self.assertEqual(len(roles), 2)

        ids = map(lambda x: x.getId(), self._roles)

        for role in roles:
            self.failUnless(role.getId() in ids)

    def testPrincipals(self):
        view = self._makeOne()
        principals = list(view.getAllPrincipals())
        self.assertEqual(len(principals), 2)

        ids = map(lambda x: x.getId(), self._principals)

        for principal in principals:
            self.failUnless(principal.getId() in ids, (principal, ids))

    def testPrincipalRoleGrid(self):
        view = self._makeOne()

        grid = view.createGrid()

        p_ids = [p.getId() for p in view.getAllPrincipals()]
        r_ids = [r.getId() for r in view.getAllRoles()]

        self.failUnless(grid.listAvailableValues())

        for p in grid.principalIds():
            self.failUnless(p in p_ids)

        for r in grid.roleIds():
            self.failUnless(r in r_ids)

        map = DummyManager()

        grid_entries = [(r, p, map.getSetting(r, p).getName())
                        for r in grid.roleIds()
                        for p in grid.principalIds()
                        ]

        for r, p, setting in grid_entries:
            self.assertEquals(setting, grid.getValue(p, r))


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
