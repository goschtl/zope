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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_modulegen.py,v 1.3 2002/12/12 10:45:53 faassen Exp $
"""

from unittest import TestCase, makeSuite, TestSuite
from Interface import Interface
from Zope.Schema import Field, Text, Int, Float, getFieldsInOrder

from Zope.App.schemagen.modulegen import generateModuleSource
    
class GenerateModuleSourceTestsBase(TestCase):

    fields = []

    def setUp(self):
        source = generateModuleSource('IFoo', self.fields, "Foo")
        self.source = source
        g = {}
        exec source in g
        del g['__builtins__'] # to ease inspection during debugging
        self.g = g
        
    def test_schema(self):
        IFoo = self.g['IFoo']
        self.assertEquals(self.fields, getFieldsInOrder(IFoo))

    def test_roundtrip(self):
        IFoo = self.g['IFoo']
        # not dealing with issues of schema inheritance,
        # so simply get all fields
        fields = getFieldsInOrder(IFoo) 
        new_source = generateModuleSource('IFoo', fields, 'Foo')
        self.assertEquals(self.source, new_source)
    
    def test_class(self):
        from Zope.Schema.FieldProperty import FieldProperty
        IFoo = self.g['IFoo']
        Foo = self.g['Foo']
        self.assertEquals(Foo.__schema_version__, 0)
        self.assertEquals(Foo.__implements__, IFoo)
        for field_name, field in self.fields:
            prop = getattr(Foo, field_name, None)
            self.assert_(prop is not None)
            self.assert_(type(prop) is FieldProperty)

    def test_instance(self):
        Foo = self.g['Foo']
        foo = Foo()
        for field_name, field in self.fields:
            self.assertEquals(field.default, getattr(foo, field_name))
        
class GenerateModuleSourceTestsEmpty(GenerateModuleSourceTestsBase):
    fields = []

class GenerateModuleSourceTests1(GenerateModuleSourceTestsBase):
    fields = [('foo', Text(title=u"Foo")),
              ('bar', Int(title=u"Bar")),
              ('hoi', Float(title=u"Float")),
              ('dag', Int(title=u"Dag", default=42)),]

def test_suite():
    return TestSuite(
        (makeSuite(GenerateModuleSourceTestsEmpty),
         makeSuite(GenerateModuleSourceTests1),
         ))

