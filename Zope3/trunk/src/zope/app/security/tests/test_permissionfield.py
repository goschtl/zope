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

$Id: test_permissionfield.py,v 1.9 2004/03/08 12:06:02 srichter Exp $
"""
import unittest
from zope.schema.interfaces import ValidationError
from zope.security.checker import CheckerPublic
from zope.app.tests import ztapi
from zope.app.security.interfaces import IPermission
from zope.app.security.permission import Permission, PermissionField
from zope.app.tests.placelesssetup import PlacelessSetup


class TestPermissionField(PlacelessSetup, unittest.TestCase):

    def test_validate(self):
        dummy = Permission('dummy', 'Dummy', 'Dummy permission')
        field = PermissionField()
        self.assertRaises(ValidationError, field.validate, dummy)
        ztapi.provideUtility(IPermission,
                             Permission('read', 'Read', 'Read something'),
                             'read')
        field.validate('read')
        field.validate(CheckerPublic)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestPermissionField),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
