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

$Id: test_add.py,v 1.13 2003/04/30 23:37:52 faassen Exp $
"""

import sys
import unittest

from zope.app.browser.form.add import add, AddViewFactory, AddView
from zope.interface import Interface
from zope.schema import TextLine, accessors
from zope.app.interfaces.container import IAdding
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.form.widget import CustomWidget
from zope.app.browser.form.widget import TextWidget as Text
from zope.publisher.browser import TestRequest
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.component import getView
from zope.component.adapter import provideAdapter
from zope.app.browser.form.submit import Update
# Foo needs to be imported as globals() are checked
from zope.app.browser.form.tests.test_editview import IFoo, IBar, Foo
from zope.app.browser.form.tests.test_editview import FooBarAdapter

class Context:

    def resolve(self, name):
        l = name.rfind('.')
        if l >= 0:
            # eek, we got a real dotted name
            m = sys.modules[name[:l]]
            return getattr(m, name[l+1:])
        else:
            return globals()[name]

class I(Interface):

    name_ = TextLine()
    first = TextLine()
    last = TextLine()
    email = TextLine()
    address = TextLine()
    getfoo, setfoo = accessors(TextLine())
    extra1 = TextLine()
    extra2 = TextLine()

class C:

    __implements__ = (I, )

    def __init__(self, *args, **kw):
        self.args = args
        self.kw = kw

    def getfoo(self): return self._foo
    def setfoo(self, v): self._foo = v

class V:
    name_ = CustomWidget(Text)
    first = CustomWidget(Text)
    last = CustomWidget(Text)
    email = CustomWidget(Text)
    address = CustomWidget(Text)
    getfoo = CustomWidget(Text)
    extra1 = CustomWidget(Text)
    extra2 = CustomWidget(Text)

class FooV:
    bar = CustomWidget(Text)


class SampleData:

    name_ = u"foo"
    first = u"bar"
    last = u"baz"
    email = u"baz@dot.com"
    address = u"aa"
    getfoo = u"foo"
    extra1 = u"extra1"
    extra2 = u"extra2"

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(IFoo, IBar, FooBarAdapter)

    def _invoke_add(self, schema="I", name="addthis", permission="zope.Public",
                    label="Add this", content_factory="C", class_="V",
                    arguments="first last", keyword_arguments="email",
                    set_before_add="getfoo", set_after_add="extra1",
                    fields=None):
        """ Call the 'add' factory to process arguments into 'args'."""
        return add(Context(),
                   schema=schema,
                   name=name,
                   permission=permission,
                   label=label,
                   content_factory=content_factory,
                   class_=class_,
                   arguments=arguments,
                   keyword_arguments=keyword_arguments,
                   set_before_add=set_before_add,
                   set_after_add=set_after_add,
                   fields=fields
                   )

    def test_add_no_fields(self):

        result1 = self._invoke_add()
        result2 = self._invoke_add(
            fields="name_ first last email address getfoo extra1 extra2",
            )

        self.assertEqual(result1, result2)

    def test_add(self, args=None):

        [(descriminator, callable, args, kw)] = self._invoke_add()

        self.assertEqual(descriminator,
                         ('view', IAdding, "addthis", IBrowserPresentation,
                          "default"))
        self.assertEqual(callable, AddViewFactory)

        (name, schema, label, permission, layer, template,
         default_template, bases, for_, fields, content_factory,
         arguments, keyword_arguments, set_before_add,
         set_after_add)  = args

        self.assertEqual(name, 'addthis')
        self.assertEqual(schema, I)
        self.assertEqual(label, 'Add this')
        self.assertEqual(permission, 'zope.Public')
        self.assertEqual(layer, 'default')
        self.assertEqual(template, 'add.pt')
        self.assertEqual(default_template, 'add.pt')
        self.assertEqual(bases, (V, AddView, ))
        self.assertEqual(for_, IAdding)
        self.assertEqual(" ".join(fields),
                         "name_ first last email address getfoo extra1 extra2")
        self.assertEqual(content_factory, C)
        self.assertEqual(" ".join(arguments),
                         "first last")
        self.assertEqual(" ".join(keyword_arguments),
                         "email")
        self.assertEqual(" ".join(set_before_add),
                         "getfoo")
        self.assertEqual(" ".join(set_after_add),
                         "extra1 name_ address extra2")
        self.failIf(kw)

        return args

    def test_create(self):

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
                     '_foo': 'foo',
                    })
                return ob
            def nextURL(self):
                return "."

        adding = Adding(self)
        [(descriminator, callable, args, kw)] = self._invoke_add()
        factory = AddViewFactory(*args)
        request = TestRequest()
        view = getView(adding, 'addthis', request)
        content = view.create('a',0,abc='def')

        self.failUnless(isinstance(content, C))
        self.assertEqual(content.args, ('a', 0))
        self.assertEqual(content.kw, {'abc':'def'})

    def test_createAndAdd(self):

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
                     '_foo': 'foo',
                    })
                return ob
            def nextURL(self):
                return "."

        adding = Adding(self)
        [(descriminator, callable, args, kw)] = self._invoke_add()
        factory = AddViewFactory(*args)
        request = TestRequest()
        view = getView(adding, 'addthis', request)

        view.createAndAdd(SampleData.__dict__)

        self.assertEqual(adding.ob.extra1, "extra1")
        self.assertEqual(adding.ob.extra2, "extra2")
        self.assertEqual(adding.ob.name_, "foo")
        self.assertEqual(adding.ob.address, "aa")

    def test_createAndAdd_w_adapter(self):

        class Adding:

            __implements__ = IAdding

            def __init__(self, test):
                self.test = test

            def add(self, ob):
                self.ob = ob
                self.test.assertEqual(ob.__dict__, {'foo': 'bar'})
                return ob
            def nextURL(self):
                return "."

        adding = Adding(self)
        [(descriminator, callable, args, kw)] = self._invoke_add(
            schema="IBar", name="addthis", permission="zope.Public",
            label="Add this", content_factory="Foo", class_="FooV",
            arguments="", keyword_arguments="",
            set_before_add="bar", set_after_add="",
            fields=None)
        factory = AddViewFactory(*args)
        request = TestRequest()
        view = getView(adding, 'addthis', request)

        view.createAndAdd({'bar': 'bar'})

    def test_hooks(self):

        class Adding:
            __implements__ = IAdding

        adding = Adding()
        [(descriminator, callable, args, kw)] = self._invoke_add()
        factory = AddViewFactory(*args)
        request = TestRequest()

        request.form.update(dict([
            ("field.%s" % k, v)
            for (k, v) in dict(SampleData.__dict__).items()
            ]))
        request.form[Update] = ''
        view = getView(adding, 'addthis', request)

        # Add hooks to V

        l=[None]

        def add(aself, ob):
            l[0] = ob
            self.assertEqual(
                ob.__dict__,
                {'args': ("bar", "baz"),
                 'kw': {'email': 'baz@dot.com'},
                 '_foo': 'foo',
                 })
            return ob

        V.add = add

        V.nextURL = lambda self: 'next'

        try:
            self.assertEqual(view.update(), '')

            self.assertEqual(view.errors, ())

            self.assertEqual(l[0].extra1, "extra1")
            self.assertEqual(l[0].extra2, "extra2")
            self.assertEqual(l[0].name_, "foo")
            self.assertEqual(l[0].address, "aa")

            self.assertEqual(request.response.getHeader("Location"), "next")

            # Verify that calling update again doesn't do anything.
            l[0] = None
            self.assertEqual(view.update(), '')
            self.assertEqual(l[0], None)

        finally:
            # Uninstall hooks
            del V.add
            del V.nextURL


def test_suite():
    return unittest.makeSuite(Test)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
