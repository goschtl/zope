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
"""$Id: test_editview.py,v 1.8 2003/04/14 08:27:15 jim Exp $
"""
import unittest

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.event.tests.placelesssetup import getEvents
from zope.interface import Interface
from zope.schema import TextLine, accessors
from zope.schema.interfaces import ITextLine
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.browser.form.editview import EditView
from zope.component.view import provideView, setDefaultViewName
from zope.component.adapter import provideAdapter
from zope.app.browser.form.widget import TextWidget
from zope.app.browser.form.submit import Update
from zope.component.exceptions import ComponentLookupError

class I(Interface):
    foo = TextLine(title=u"Foo")
    bar = TextLine(title=u"Bar")
    a   = TextLine(title=u"A")
    b   = TextLine(title=u"B")
    getbaz, setbaz = accessors(TextLine(title=u"Baz"))

class EV(EditView):
    schema = I

class C:
    __implements__ = (I, )
    foo = u"c foo"
    bar = u"c bar"
    a   = u"c a"
    b   = u"c b"
    
    _baz = u"c baz"
    def getbaz(self): return self._baz
    def setbaz(self, v): self._baz = v


class IFoo(Interface):
    foo = TextLine(title=u"Foo")
    
class IBar(Interface):
    bar = TextLine(title=u"Bar")

class Foo:
    __implements__ = IFoo

    foo = 'Foo foo'

class FooBarAdapter(object):

    def __init__(self, context):
        self.context = context

    def setbar(self, v):
        self.context.foo = v

    bar = property(lambda self: self.context.foo,
                   setbar)

class BarV(EditView):
    schema = IBar

class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideView(ITextLine, 'edit', IBrowserPresentation, TextWidget)
        setDefaultViewName(ITextLine, IBrowserPresentation, "edit")
        provideAdapter(IFoo, IBar, FooBarAdapter)

    def test_setPrefix_and_widgets(self):
        v = EV(C(), TestRequest())
        v.setPrefix("test")
        self.assertEqual(
            [w.name for w in v.widgets()],
            ['test.foo', 'test.bar', 'test.a', 'test.b', 'test.getbaz']
            )

    def test_apply_update_no_data(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        d = {}
        d['foo'] = u'c foo'
        d['bar'] = u'c bar'
        d['getbaz'] = u'c baz'
        self.failUnless(v.apply_update(d))
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.getbaz(), u'c baz')
        self.failIf(getEvents())

    def test_apply_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        d = {}
        d['foo'] = u'd foo'
        d['bar'] = u'd bar'
        d['getbaz'] = u'd baz'
        self.failIf(v.apply_update(d))
        self.assertEqual(c.foo, u'd foo')
        self.assertEqual(c.bar, u'd bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.getbaz(), u'd baz')
        self.failUnless(getEvents(filter=lambda event: event.object == c))

    def test_apply_update_w_adapter(self):
        c = Foo()
        request = TestRequest()
        v = BarV(c, request)
        d = {}
        d['bar'] = u'd bar'
        self.failIf(v.apply_update(d))
        self.assertEqual(c.foo, u'd bar')

        # We should not get events whan an adapter is used. That's the
        # adapter's job.
        self.failIf(getEvents())

    def test_fail_wo_adapter(self):
        c = Foo()
        request = TestRequest()
        self.assertRaises(ComponentLookupError, EV, c, request)

    def test_update_no_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        self.assertEqual(v.update(), '')
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.getbaz(), u'c baz')
        request.form['field.foo'] = u'r foo'
        request.form['field.bar'] = u'r bar'
        request.form['field.a']   = u'r a'
        request.form['field.b']   = u'r b'
        request.form['field.getbaz'] = u'r baz'
        self.assertEqual(v.update(), '')
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.getbaz(), u'c baz')
        self.failIf(getEvents())

    def test_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        request.form[Update] = ''
        request.form['field.foo'] = u'r foo'
        request.form['field.bar'] = u'r bar'
        request.form['field.getbaz'] = u'r baz'
        request.form['field.a'] = u'c a'

        message = v.update()
        self.failUnless(message.startswith('Updated '), message)
        self.assertEqual(c.foo, u'r foo')
        self.assertEqual(c.bar, u'r bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , None)
        self.assertEqual(c.getbaz(), u'r baz')

        # Verify that calling update multiple times has no effect

        c.__dict__.clear()
        self.assertEqual(v.update(), message)
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.getbaz(), u'c baz')




def test_suite():
    return unittest.makeSuite(Test)

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
