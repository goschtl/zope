##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Permission fields tests

$Id: testPermissionField.py,v 1.2 2002/12/21 20:17:56 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Security.PermissionField import PermissionField
from Zope.Schema.Exceptions import ValidationError
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.App.Security.Registries.PermissionRegistry import permissionRegistry
from Zope.App.Security.IPermissionService import IPermissionService
from Zope.ComponentArchitecture.GlobalServiceManager \
     import serviceManager, defineService
from Zope.App.Security.Registries.PermissionRegistry import Permission

class TestPermissionField(PlacelessSetup, TestCase):

    def test_validate(self):
        defineService("Permissions", IPermissionService)
        serviceManager.provideService("Permissions", permissionRegistry)
        dummy = Permission('dummy', 'Dummy', 'Dummy permission')
        field = PermissionField()
        self.assertRaises(ValidationError, field.validate, dummy)
        permissionRegistry.definePermission('read', 'Read', 'Read something')
        field.validate(permissionRegistry.getPermission('read'))

def test_suite():
    return TestSuite((makeSuite(TestPermissionField),))


if __name__=='__main__':
    main(defaultTest='test_suite')

