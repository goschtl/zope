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

$Id: test_field.py,v 1.6 2003/03/13 17:10:37 gvanrossum Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.schema.interfaces import ValidationError
from zope.interface import Interface

from zope.app.interfaces.services.module import IModuleService
from zope.component.interfaces import IServiceService

class ModuleService:
    __implements__ = IModuleService, IServiceService
    # I'm lying about implementing IServiceService, but that is needed to get
    # a ModuleService as a service manager.  (See XXX comment in module.py.)
    def __init__(self, name=None, component=None):
        self.lookup = {}
        if name is not None:
            self.lookup[name] = component
    def resolve(self, dotted_name):
        if self.lookup.has_key(dotted_name):
            return self.lookup[dotted_name]
        raise ImportError, dotted_name

    def getService(self, name):
        from zope.component import getService
        return getService(None, name)

class I1(Interface):  pass

class C:
    __implements__ = I1

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

class TestComponentLocation(TestComponentPath):

    def createObjects(self):
        TestComponentPath.createObjects(self)
        self.resolver = ModuleService()
        self.rootFolder.setServiceManager(self.resolver)

    def createFields(self):
        from zope.app.services.field import ComponentLocation

        folder2 = traverse(self.rootFolder, 'folder2')
        field = ComponentLocation(type=I1)
        field = field.bind(folder2)
        self.field = field
        notypefield = ComponentLocation(type=None)
        notypefield = notypefield.bind(folder2)
        self.notypefield = notypefield

    def test__validateDottedName(self):
        field = self.notypefield
        dotted_name = u'zope.app.whatever.ClassName'
        some_class = self.__class__
        self.resolver.lookup[dotted_name] = some_class
        field._validate(dotted_name)
        self.assertRaises(ValidationError, field._validate, u'foo.bar.baz')

class TestLocateComponent(PlacefulSetup, TestCase):

    def test_locateComponent(self):
        from zope.app.services.field import locateComponent

        self.buildFolders()
        self.folder1.setObject('c', C())
        self.folder1.setObject('d', D())

        folder2 = traverse(self.rootFolder, 'folder2')

        self.assertEqual(locateComponent(u'/folder1/c', folder2, I1),
                         traverse(self.rootFolder, '/folder1/c')
                         )
        self.assertRaises(ValidationError,
                          locateComponent, u'/folder1/d', folder2, I1)
        self.assertRaises(ValidationError,
                          locateComponent, u'/folder1/e', folder2)

        dotted_name = 'zope.app.whatever.ClassName'
        some_class = self.__class__
        resolver = ModuleService(dotted_name, some_class)
        self.rootFolder.setServiceManager(resolver)
        self.assertEqual(locateComponent(dotted_name, folder2),
                         some_class
                         )
        self.assertRaises(ValidationError, locateComponent, 'f.b.b', folder2)

def test_suite():
    return TestSuite((
        makeSuite(TestComponentPath),
        makeSuite(TestComponentLocation),
        makeSuite(TestLocateComponent),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
