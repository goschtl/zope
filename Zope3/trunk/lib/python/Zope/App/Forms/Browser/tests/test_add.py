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
"""

$Id: test_add.py,v 1.2 2002/12/19 20:15:31 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from Zope.App.Forms.Browser.add import add, AddViewFactory, AddView
from Interface import Interface
from Zope.Schema import TextLine
from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.Forms.Widget import CustomWidget
from Zope.App.Forms.Views.Browser.Widget import TextWidget as Text
from Zope.Publisher.Browser.BrowserRequest import TestRequest
from Zope.App.tests.PlacelessSetup import PlacelessSetup
from Zope.ComponentArchitecture import getView

class Context:

    def resolve(self, name):
        return globals()[name]

class I(Interface):
    
    name = TextLine()
    first = TextLine()
    last = TextLine()
    email = TextLine()
    address = TextLine()
    foo = TextLine()
    extra1 = TextLine()
    extra2 = TextLine()

class C:

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

class V:
    name = CustomWidget(Text)
    first = CustomWidget(Text)
    last = CustomWidget(Text)
    email = CustomWidget(Text)
    address = CustomWidget(Text)
    foo = CustomWidget(Text)
    extra1 = CustomWidget(Text)
    extra2 = CustomWidget(Text)

    
class SampleData:

    name = "foo"
    first = "bar"
    last = "baz"
    email = "baz@dot.com"
    address = "aa"
    foo = "foo"
    extra1 = "extra1"
    extra2 = "extra2"

class Test(PlacelessSetup, TestCase):

    def test_add_no_fields(self):

        result1 = add(
            Context(),
            schema="I",
            name="addthis",
            permission="Zope.Public",
            label="Add this",
            content_factory="C",
            arguments="first last",
            keyword_arguments="email",
            set_before_add="foo",
            set_after_add="extra1",
            )

        result2 = add(
            Context(),
            schema="I",
            name="addthis",
            permission="Zope.Public",
            label="Add this",
            content_factory="C",
            arguments="first last",
            keyword_arguments="email",
            set_before_add="foo",
            set_after_add="extra1",
            fields="name first last email address foo extra1 extra2",
            )

        self.assertEqual(result1, result2)

    def test_add(self):

        [(descriminator, callable, args, kw)] = add(
            Context(),
            schema="I",
            name="addthis",
            permission="Zope.Public",
            label="Add this",
            content_factory="C",
            class_="V",
            arguments="first last",
            keyword_arguments="email",
            set_before_add="foo",
            set_after_add="extra1",
            )


        self.assertEqual(descriminator,
                         ('http://namespaces.zope.org/form/add',
                          "addthis", "default"))
        self.assertEqual(callable, AddViewFactory)

        (name, schema, label, permission, layer, template,
         default_template, bases, for_, fields, content_factory,
         arguments, keyword_arguments, set_before_add,
         set_after_add)  = args

        self.assertEqual(name, 'addthis')
        self.assertEqual(schema, I)
        self.assertEqual(label, 'Add this')
        self.assertEqual(permission, 'Zope.Public')
        self.assertEqual(layer, 'default')
        self.assertEqual(template, 'add.pt')
        self.assertEqual(default_template, 'add.pt')
        self.assertEqual(bases, (V, AddView, ))
        self.assertEqual(for_, IAdding)
        self.assertEqual(" ".join(fields),
                         "name first last email address foo extra1 extra2")
        self.assertEqual(content_factory, C)
        self.assertEqual(" ".join(arguments), 
                         "first last")
        self.assertEqual(" ".join(keyword_arguments), 
                         "email")
        self.assertEqual(" ".join(set_before_add), 
                         "foo")
        self.assertEqual(" ".join(set_after_add), 
                         "extra1 name address extra2")
        self.failIf(kw)

        return args

    def test_apply_update(self):

        class Adding:

            __implements__ = IAdding

            def __init__(self, test):
                self.test = test
            
            def add(self, ob):
                self.ob = ob
                self.test.assertEqual(
                    ob.__dict__,
                    {'args': ("bar", "baz"),
                     'kw': {'email': 'baz@dot.com'},
                     'foo': 'foo',
                    })
                return ob
            def nextURL(self):
                return "."
            
        adding = Adding(self)
        args = self.test_add()
        factory = AddViewFactory(*args)
        request = TestRequest()
        request.form.update(SampleData.__dict__)
        view = getView(adding, 'addthis', request)
        view.apply_update(SampleData.__dict__)

        self.assertEqual(adding.ob.extra1, "extra1")
        self.assertEqual(adding.ob.extra2, "extra2")
        self.assertEqual(adding.ob.name, "foo")
        self.assertEqual(adding.ob.address, "aa")

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
