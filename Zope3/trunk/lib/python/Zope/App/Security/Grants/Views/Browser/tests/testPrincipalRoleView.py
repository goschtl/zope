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

$Id: testPrincipalRoleView.py,v 1.2 2002/06/25 15:27:52 efge Exp $
"""

import unittest

from Zope.App.OFS.Services.ServiceManager.tests.PlacefulSetup\
           import PlacefulSetup
from Zope.ComponentArchitecture import getServiceManager

from Zope.App.Security.IRoleService import IRoleService
from Zope.App.Security.IAuthenticationService import IAuthenticationService

from Zope.App.Security.IPrincipalRoleManager import IPrincipalRoleManager
from Zope.App.Security.IPrincipalRoleMap import IPrincipalRoleMap

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

    __implements__ = IRoleService

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

    __implements__ = IAuthenticationService

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

        defineService('RoleService', IRoleService)
        provideService('RoleService'
                      , DummyRoleService(roles = self._roles))

        defineService('AuthenticationService', IAuthenticationService)

        self._principals = []
        self._principals.append(DummyObject('foo', 'Foo'))
        self._principals.append(DummyObject('bar', 'Bar'))

        provideService('AuthenticationService',
            DummyAuthenticationService(principals = self._principals))

    def _makeOne(self):
        from Zope.App.Security.Grants.Views.Browser.PrincipalRoleView \
             import PrincipalRoleView
        return PrincipalRoleView(DummyManager(), None)

    def testRoles(self):
        view = self._makeOne()
        roles = list(view.getAllRoles())
        self.assertEqual(len(roles), 2)

        ids = map(lambda x: x.getId(), self._roles)

        for role in roles:
            self.failUnless(role in ids)

    def testPrincipals(self):
        view = self._makeOne()
        principals = list(view.getAllPrincipals())
        self.assertEqual(len(principals), 2)

        ids = map(lambda x: x.getId(), self._principals)

        for principal in principals:
            self.failUnless(principal in ids)

    def testPrincipalRoleGrid(self):
        view = self._makeOne()

        grid = view.createGrid()

        p_ids = [p.getId() for p in view.getAllPrincipals()]
        r_ids = [r.getId() for r in view.getAllRoles()]

        self.failUnless(grid.listAvailableValues())

        for id in grid.principals():
            self.failUnless(id in p_ids)

        for id in grid.roles():
            self.failUnless(id in r_ids)

        map = DummyManager()

        grid_entries = [(r, p, map.getSetting(r, p).getName())
            for r in grid.roles()
            for p in grid.principals()]

        for r, p, setting in grid_entries:
            self.assertEquals(setting, grid.getValue(p, r))


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
