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

$Id: test_typereg.py,v 1.2 2002/12/12 10:45:53 faassen Exp $
"""

from unittest import TestCase, makeSuite, TestSuite
import datetime

from Zope.App.schemagen.typereg import TypeRepresentationRegistry,\
     DefaultTypeRepresentation, DatetimeRepresentation,\
     DefaultFieldRepresentation

from Zope import Schema

from Zope.Schema.IField import IField
from Zope.Schema import Field, Text, Int

class DefaultTypeRepresentationTests(TestCase):
    def test_getTypes(self):
        c = DefaultTypeRepresentation
        self.assertEquals((), tuple(c.getTypes()))

    def h(self, obj):
        r = DefaultTypeRepresentation(obj)
        self.assertEquals(eval(r.text), obj)
    
    def h_builtin(self, obj):
        r = DefaultTypeRepresentation(obj)
        self.assertEquals(eval(r.text), obj)
        self.assertEquals([], r.importList)

    builtin_instances = [
        'foo',
        1,
        1.1,
        (),
        (1, "foo"),
        [],
        [5, 2],
        {},
        {'foo':'bar', 'baz':'hoi'},
        {'foo': (1, "foo")}
        ]
    
    def test_builtins(self):
        for builtin_instance in self.builtin_instances:
            self.h_builtin(builtin_instance)

    def test_recursive(self):
        # we cannot cope with recursive structures
        recursive = [1, 2]
        recursive.append(recursive)
        r = DefaultTypeRepresentation(recursive)
        self.assertRaises(SyntaxError, eval, r.text)

class DatetimeRepresentationTests(TestCase):

    datetime_instances = [
        (datetime.date(2002, 10, 30),
         [('datetime', 'date')]),
        (datetime.datetime(2002, 10, 30, 11, 44, 10),
         [('datetime', 'datetime')]),
        (datetime.time(10, 0, 1),
         [('datetime', 'time')]),
        ]
    
    def test_date(self):
        for datetime_instance, import_list in self.datetime_instances:
            r = DatetimeRepresentation(datetime_instance)
            self.assertEquals(datetime_instance, evalRepresentation(r))
            r_imports = r.importList
            r_imports.sort()
            import_list.sort()
            self.assertEquals(r_imports, import_list)

def evalRepresentation(r):
    import_dict = {}
    for import_name, import_from in r.importList:
        module = __import__(import_name, {}, {}, [import_from])
        import_dict[import_from] = getattr(module, import_from)
    return eval(r.text, import_dict)

class TypeRepresentationRegistryTests(TestCase):
    def setUp(self):
        self.tr = TypeRepresentationRegistry(DefaultTypeRepresentation)

    def test_default(self):
        self.assert_(isinstance(
            self.tr.represent(1), DefaultTypeRepresentation))
        
    def test_register(self):
        from Zope.App.schemagen.interfaces import ITypeRepresentation
        class IntRepresentation:
            __implements__ = ITypeRepresentation
            def __init__(self, obj):
                pass
            def getTypes():
                return (int,)

            getTypes = staticmethod(getTypes)

            importList = []
            text = ''
            
        self.tr.register(IntRepresentation)
        self.assert_(isinstance(self.tr.represent(1), IntRepresentation))

        self.assert_(isinstance(self.tr.represent('foo'),
                                DefaultTypeRepresentation))

class IFieldSchema(IField):
    # the greek alphabet is not in alphabetical order, so we cannot
    # depend on ascii sort order, which is good as we shouldn't.
    alpha = Text(title=u"Alpha", default=u"")
    beta = Int(title=u"Beta", default=0)
    gamma = Text(title=u"Gamma", default=u"")
    delta = Int(title=u"Delta", default=0)

class MyField(Field):
    __implements__ = IFieldSchema

    def __init__(self, alpha=u'', beta=0, gamma=u'', delta=0, **kw):
        super(MyField, self).__init__(**kw)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        
class DefaultFieldRepresentationTests(TestCase):
    # XXX there is an issue with field classes which have the same name
    # multiple 'from x import y' statements will cause one name to be
    # shadowed by another. We can't test for this yet.

    schema_fields = [
        (Schema.Text(title=u"text"),
         [('Zope.Schema', 'Text')]),
        (Schema.Int(title=u"int"),
         [('Zope.Schema', 'Int')]),
        (Schema.TextLine(title=u"text"),
         [('Zope.Schema', 'TextLine')]),
        (Schema.Float(title=u"float"),
         [('Zope.Schema', 'Float')])
        ]
    
    def test_field(self):
        for field, import_list in self.schema_fields:
            r = DefaultFieldRepresentation(field)
            self.assertEquals(field, evalRepresentation(r))
            r_imports = r.importList
            r_imports.sort()
            import_list.sort()
            self.assertEquals(r_imports, import_list)

    def test_order(self):
        field = MyField(alpha=u'alpha', gamma=u'gamma', delta=23)
        r = DefaultFieldRepresentation(field)
        t = r.text
        a = t.find('alpha')
        g = t.find('gamma')
        d = t.find('delta')
        self.assertNotEquals(a, -1)
        self.assertNotEquals(g, -1)
        self.assertNotEquals(d, -1)
        self.assert_(a < g < d)
    
def test_suite():
    return TestSuite(
        (makeSuite(DefaultTypeRepresentationTests),
         makeSuite(DatetimeRepresentationTests),
         makeSuite(TypeRepresentationRegistryTests),
         makeSuite(DefaultFieldRepresentationTests),
        ))
