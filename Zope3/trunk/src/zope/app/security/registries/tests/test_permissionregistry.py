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
""" Test handler for 'definePermission' directive

$Id: test_permissionregistry.py,v 1.3 2003/05/01 19:35:33 faassen Exp $
"""


import unittest

from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.security.exceptions import UndefinedPermissionError
from zope.app.interfaces.security import IPermission
from zope.interface.verify import verifyObject
from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class Test(CleanUp, unittest.TestCase):

    def testEmptyPermissions(self):
        self.assertEqual(None, permissionRegistry.getPermission('Foo'))
        self.failIf(permissionRegistry.definedPermission('Foo'))

    def testPermissionStartsWithDot(self):
        self.assertRaises(ValueError, permissionRegistry.definePermission,
                          '.Foo', 'dot foo title')

    def testPermissionIsAnIPermission(self):
        permissionRegistry.definePermission('Foo', 'foo title')
        permission = permissionRegistry.getPermission('Foo')
        self.assertEqual(verifyObject(IPermission, permission), 1)

    def testDefinePermission(self):
        perm = permissionRegistry.definePermission('Foo', 'foo title')
        self.failUnless(verifyObject(IPermission, perm))
        self.failUnless(permissionRegistry.definedPermission('Foo'))
        permission = permissionRegistry.getPermission('Foo')
        self.assertEquals(permission.getTitle(), 'foo title')

    def testDefinePermissionWithTitle(self):
        eq = self.assertEqual
        permissionRegistry.definePermission('Foo', 'Foo-able')
        permission = permissionRegistry.getPermission('Foo')
        eq(permission.getTitle(), 'Foo-able')
        eq(permission.getDescription(), '')

    def testDefinePermissionWithTitleAndDescription(self):
        eq = self.assertEqual
        permissionRegistry.definePermission('Foo', 'Foo-able',
                                            'A foo-worthy permission')
        permission = permissionRegistry.getPermission('Foo')
        eq(permission.getTitle(), 'Foo-able')
        eq(permission.getDescription(), 'A foo-worthy permission')

    def testEnsurePermissionDefined(self):
        permissionRegistry.definePermission('Foo', 'Foo-able',
                                            'A foo-worthy permission')
        self.assertEqual(None,
                         permissionRegistry.ensurePermissionDefined('Foo'))
        self.assertRaises(UndefinedPermissionError,
                          permissionRegistry.ensurePermissionDefined,
                          'Foo.Bar.Spam.Undefined')


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)


if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
