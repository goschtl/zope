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
""" Test handler for 'defineRole' directive """

import unittest

from zope.app.security.registries.roleregistry import roleRegistry
from zope.app.interfaces.security import IRole
from zope.interface.verify import verifyObject
from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class Test(CleanUp, unittest.TestCase):

    def testEmptyRoles(self):
        self.assertEqual(None, roleRegistry.getRole('Foo'))
        self.failIf(roleRegistry.definedRole('Foo'))

    def testRoleIsAnIRole(self):
        r = roleRegistry.defineRole('Foo', 'Foo role')
        role = roleRegistry.getRole(r.getId())
        self.assertEqual(verifyObject(IRole, role), 1)

    def testDefineRole(self):
        role = roleRegistry.defineRole('Foo', 'foo role')
        self.failUnless(verifyObject(IRole, role))
        self.failUnless(roleRegistry.definedRole(role.getId()))
        role = roleRegistry.getRole(role.getId())
        self.assertEquals(role.getTitle(), 'foo role')

    def testDefineRoleWithTitle(self):
        eq = self.assertEqual
        r = roleRegistry.defineRole('Foo', 'Foo-able')
        role = roleRegistry.getRole(r.getId())
        eq(role.getTitle(), 'Foo-able')
        eq(role.getDescription(), '')

    def testDefineRoleWithTitleAndDescription(self):
        eq = self.assertEqual
        r = roleRegistry.defineRole('Foo', 'Foo-able', 'A foo-worthy role')
        role = roleRegistry.getRole(r.getId())
        eq(role.getTitle(), 'Foo-able')
        eq(role.getDescription(), 'A foo-worthy role')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
