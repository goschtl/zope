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

$Id: test_modulegen.py,v 1.1 2002/12/11 19:07:23 faassen Exp $
"""

from unittest import TestCase, makeSuite, TestSuite
from Interface import Interface
from Zope.Schema import Text, Int, Float, getFields

from Zope.App.schemagen.modulegen import generateModuleSource
    
class GenerateModuleSourceTestsBase(TestCase):

    fields = []

    def test_generateModuleSource(self):
        
        source = generateModuleSource('IFoo', self.fields, "Foo")
        g = {}
        exec source in g
        del g['__builtins__'] # to ease inspection during debugging
        IFoo = g['IFoo']

        fieldsorter = lambda x, y: cmp(x[1].order, y[1].order)
        new_fields = getFields(IFoo).items()
        new_fields.sort(fieldsorter)
        self.assertEquals(self.fields, new_fields)

    # XXX we'd like to test the whole roundtrip eventually,
    # by execing generated module source again and then generating
    # module source for the schema in that. This requires the arguments
    # to fields (their properties) to be in their own schema order.
    
class GenerateModuleSourceTestsEmpty(GenerateModuleSourceTestsBase):
    fields = []

class GenerateModuleSourceTests1(GenerateModuleSourceTestsBase):
    fields = [('foo', Text(title=u"Foo")),
              ('bar', Int(title=u"Bar")),
              ('hoi', Float(title=u"Float"))]
    
def test_suite():
    return TestSuite(
        (makeSuite(GenerateModuleSourceTestsEmpty),
         makeSuite(GenerateModuleSourceTests1)
         ))

