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
"""Principal-Role View Tests

$Id$
"""
import unittest

from zope.interface import implements
from zope.publisher.browser import TestRequest
from zope.app.publisher.browser import BrowserView

from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.security.interfaces import IAuthenticationService, IPrincipal
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission
from zope.app.site.interfaces import ISimpleService
from zope.app.servicenames import Authentication
from zope.app.site.tests.placefulsetup import PlacefulSetup

from zope.app.securitypolicy.role import Role
from zope.app.securitypolicy.interfaces import IRole
from zope.app.securitypolicy.interfaces import IPrincipalRoleManager
from zope.app.securitypolicy.browser.principalroleview import \
     PrincipalRoleView

class PrincipalRoleView(PrincipalRoleView, BrowserView):
    """Adding BrowserView to Utilities; this is usually done by ZCML."""

class DummySetting(object):
    def __init__(self, name):
        self._name = name
    def getName(self):
        return self._name

class DummyManager(object):

    implements(IPrincipalRoleManager)

    def getSetting(self, role, principal):
        return DummySetting('%r:%r' % (role, principal))

class DummyAuthenticationService(object):

    implements(IAuthenticationService, ISimpleService)

    def __init__(self, principals):
        self._principals = principals

    def getPrincipals(self, name):
        return self._principals

class DummyPrincipal(object):
    implements(IPrincipal)

    def __init__(self, id, title):
        self.id = id
        self.title = title


def defineRole(id, title=None, description=None):
    role = Role(id, title, description)
    ztapi.provideUtility(IRole, role, name=role.id)
    return role


class Test(PlacefulSetup, unittest.TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)

        self._roles = [defineRole('qux', 'Qux'), defineRole('baz', 'Baz')]

        sm = zapi.getGlobalServices()

        sm.defineService(Authentication, IAuthenticationService)

        self._principals = []
        self._principals.append(DummyPrincipal('foo', 'Foo'))
        self._principals.append(DummyPrincipal('bar', 'Bar'))

        sm.provideService(Authentication,
            DummyAuthenticationService(principals = self._principals))

    def _makeOne(self):
        return PrincipalRoleView(DummyManager(), TestRequest())

    def testRoles(self):
        view = self._makeOne()
        roles = list(view.getAllRoles())
        self.assertEqual(len(roles), 2)

        ids = [role.id for role in self._roles]

        for role in roles:
            self.failUnless(role.id in ids)

    def testPrincipals(self):
        view = self._makeOne()
        principals = list(view.getAllPrincipals())
        self.assertEqual(len(principals), 2)

        ids = [p.id for p in self._principals]

        for principal in principals:
            self.failUnless(principal.id in ids, (principal, ids))

    def testPrincipalRoleGrid(self):
        view = self._makeOne()

        grid = view.createGrid()

        p_ids = [p.id for p in view.getAllPrincipals()]
        r_ids = [r.id for r in view.getAllRoles()]

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
