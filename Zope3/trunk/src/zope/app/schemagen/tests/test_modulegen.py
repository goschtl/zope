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
"""
$Id: test_modulegen.py,v 1.5 2004/02/20 16:57:29 fdrake Exp $
"""

from unittest import TestCase, makeSuite, TestSuite
from zope.schema import Text, Int, Float, getFieldsInOrder
from zope.interface import implementedBy
from persistent.interfaces import IPersistent
from zope.app.schemagen.modulegen import generateModuleSource

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
        from zope.schema.fieldproperty import FieldProperty
        IFoo = self.g['IFoo']
        Foo = self.g['Foo']
        # we don't want a schema version attribute on the class, just
        # on the individual instances
        self.assertRaises(AttributeError, getattr, Foo, '__schema_version__')
        self.assertEquals([i for i in implementedBy(Foo)],
                          [IFoo, IPersistent])
        for field_name, field in self.fields:
            prop = getattr(Foo, field_name, None)
            self.assert_(prop is not None)
            self.assert_(type(prop) is FieldProperty)

    def test_instance(self):
        Foo = self.g['Foo']
        foo = Foo()
        self.assertEquals(foo.__schema_version__, 0)
        for field_name, field in self.fields:
            self.assertEquals(field.default, getattr(foo, field_name))

class GenerateModuleSourceTestsEmpty(GenerateModuleSourceTestsBase):
    fields = []

class GenerateModuleSourceTests1(GenerateModuleSourceTestsBase):
    fields = [('foo', Text(title=u"Foo")),
              ('bar', Int(title=u"Bar")),
              ('hoi', Float(title=u"Float")),
              ('dag', Int(title=u"Dag", default=42)),]

class ExtraImportsAndMethodsTests(TestCase):
    fields = [('foo', Text(title=u"Foo")),
              ('bar', Int(title=u"Bar")),
              ('hoi', Float(title=u"Float")),
              ('dag', Int(title=u"Dag", default=42)),]

    def test_extraMethods(self):
        extra_methods = """\
    def forGreatJustice(self):
        return 'zig!'
"""
        source = generateModuleSource('IFoo', self.fields, "Foo",
                                      extra_methods=extra_methods)
        g = {}
        exec source in g
        del g['__builtins__'] # to ease inspection during debugging
        foo = g['Foo']()
        self.assertEquals('zig!', foo.forGreatJustice())

    def test_extraImports(self):
        # we import ourselves, as then there's no dependencies
        from zope.app.schemagen.tests import test_modulegen
        extra_imports = "from zope.app.schemagen.tests import test_modulegen"
        source = generateModuleSource('IFoo', self.fields, "Foo",
                                      extra_imports=extra_imports)
        g = {}
        exec source in g
        del g['__builtins__'] # to ease inspection during debugging
        self.assert_(g['test_modulegen'] is test_modulegen)

def test_suite():
    return TestSuite(
        (makeSuite(GenerateModuleSourceTestsEmpty),
         makeSuite(GenerateModuleSourceTests1),
         makeSuite(ExtraImportsAndMethodsTests),
         ))
