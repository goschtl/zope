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

$Id: test_field.py,v 1.3 2003/01/09 17:28:46 stevea Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.schema.interfaces import ValidationError
from zope.interface import Interface
from zope.app.services.field import ComponentPath

class I1(Interface):  pass

class C:
    __implements__ = I1

class D:
    pass

class Test(PlacefulSetup, TestCase):

    def test__validate(self):
        self.buildFolders()
        self.folder1.setObject('c', C())
        self.folder1.setObject('d', D())

        folder2 = traverse(self.rootFolder, 'folder2')

        field = ComponentPath(type=I1)
        field = field.bind(folder2)

        field.validate(u'/folder1/c')

        self.assertRaises(ValidationError, field.validate, u'/folder1/d')
        self.assertRaises(ValidationError, field.validate, u'/folder1/e')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
