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

$Id: test_permissionfield.py,v 1.4 2003/01/21 21:21:47 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.security.permission import PermissionField
from zope.schema.interfaces import ValidationError
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.security.registries.permissionregistry import permissionRegistry
from zope.app.interfaces.security import IPermissionService
from zope.component.service \
     import serviceManager, defineService
from zope.app.security.registries.permissionregistry import Permission

class TestPermissionField(PlacelessSetup, TestCase):

    def test_validate(self):
        defineService("Permissions", IPermissionService)
        serviceManager.provideService("Permissions", permissionRegistry)
        dummy = Permission('dummy', 'Dummy', 'Dummy permission')
        field = PermissionField()
        self.assertRaises(ValidationError, field.validate, dummy)
        permissionRegistry.definePermission('read', 'Read', 'Read something')
        field.validate(permissionRegistry.getPermission('read').getId())

def test_suite():
    return TestSuite((makeSuite(TestPermissionField),))


if __name__=='__main__':
    main(defaultTest='test_suite')
