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
"""Tests for ComponentPath field.

$Id: test_field.py,v 1.10 2003/07/04 10:59:21 ryzaja Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.schema.interfaces import ValidationError
from zope.interface import Interface, implements

from zope.component.interfaces import IServiceService

class I1(Interface):  pass

class C:
    implements(I1)

class D:
    pass

class TestComponentPath(PlacefulSetup, TestCase):

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.createObjects()
        self.createFields()

    def createObjects(self):
        self.buildFolders()
        self.folder1.setObject('c', C())
        self.folder1.setObject('d', D())

    def createFields(self):
        from zope.app.services.field import ComponentPath

        folder2 = traverse(self.rootFolder, 'folder2')
        field = ComponentPath(type=I1)
        field = field.bind(folder2)
        self.field = field

    def test__validate(self):
        field = self.field
        field.validate(u'/folder1/c')

        self.assertRaises(ValidationError, field.validate, u'/folder1/d')
        self.assertRaises(ValidationError, field.validate, u'/folder1/e')

def test_suite():
    return TestSuite((
        makeSuite(TestComponentPath),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
