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

$Id: test_modulegen.py,v 1.2 2002/12/12 09:17:46 faassen Exp $
"""

from unittest import TestCase, makeSuite, TestSuite
from Interface import Interface
from Zope.Schema import Text, Int, Float, getFields

from Zope.App.schemagen.modulegen import generateModuleSource
    
class GenerateModuleSourceTestsBase(TestCase):

    fields = []

    def setUp(self):
        source = generateModuleSource('IFoo', self.fields, "Foo")
        g = {}
        exec source in g
        del g['__builtins__'] # to ease inspection during debugging
        self.g = g
        
    def test_schema(self):
        IFoo = self.g['IFoo']

        fieldsorter = lambda x, y: cmp(x[1].order, y[1].order)
        new_fields = getFields(IFoo).items()
        new_fields.sort(fieldsorter)
        self.assertEquals(self.fields, new_fields)

    # XXX we'd like to test the whole roundtrip eventually,
    # by execing generated module source again and then generating
    # module source for the schema in that. This requires the arguments
    # to fields (their properties) to be in their own schema order.

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
         makeSuite(GenerateModuleSourceTests1)
         ))

