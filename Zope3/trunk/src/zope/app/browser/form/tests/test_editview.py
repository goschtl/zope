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
"""$Id: test_editview.py,v 1.4 2003/03/02 03:34:05 tseaver Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app.event.tests.placelesssetup import getEvents
from zope.interface import Interface
from zope.schema import TextLine
from zope.schema.interfaces import ITextLine
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserPresentation
from zope.app.browser.form.editview import EditView
from zope.component.view \
     import provideView, setDefaultViewName
from zope.app.browser.form.widget import TextWidget
from zope.app.browser.form.submit import Update

class I(Interface):
    foo = TextLine(title=u"Foo")
    bar = TextLine(title=u"Bar")
    a   = TextLine(title=u"A")
    b   = TextLine(title=u"B")
    baz = TextLine(title=u"Baz")

class EV(EditView):
    schema = I

class C:
    __implements__ = ( I, )
    foo = u"c foo"
    bar = u"c bar"
    a   = u"c a"
    b   = u"c b"
    baz = u"c baz"

class NonConforming( C ):
    __implements__ = ()

class Test(PlacelessSetup, TestCase):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideView(ITextLine, 'edit', IBrowserPresentation, TextWidget)
        setDefaultViewName(ITextLine, IBrowserPresentation, "edit")

    def test_setPrefix_and_widgets(self):
        v = EV(C(), TestRequest())
        v.setPrefix("test")
        self.assertEqual(
            [w.name for w in v.widgets()],
            ['test.foo', 'test.bar', 'test.a', 'test.b', 'test.baz']
            )

    def test_apply_update_no_data(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        d = {}
        d['foo'] = u'c foo'
        d['bar'] = u'c bar'
        d['baz'] = u'c baz'
        self.failUnless(v.apply_update(d))
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.baz, u'c baz')
        self.failIf(getEvents())

    def test_apply_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        d = {}
        d['foo'] = u'd foo'
        d['bar'] = u'd bar'
        d['baz'] = u'd baz'
        self.failIf(v.apply_update(d))
        self.assertEqual(c.foo, u'd foo')
        self.assertEqual(c.bar, u'd bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.baz, u'd baz')
        self.failUnless(getEvents(filter=lambda event: event.object == c))

    def test_apply_update_w_non_conforming_context(self):
        # XXX   This feels bogus:  why should we be used to edit a context
        #       which doesn't implement our schema?
        c = NonConforming()
        request = TestRequest()
        v = EV(c, request)
        d = {}
        d['foo'] = u'd foo'
        d['bar'] = u'd bar'
        d['baz'] = u'd baz'
        self.failIf(v.apply_update(d))
        self.assertEqual(c.foo, u'd foo')
        self.assertEqual(c.bar, u'd bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.baz, u'd baz')
        self.failUnless(getEvents(filter=lambda event: event.object == c))

    def test_update_no_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        self.assertEqual(v.update(), '')
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.baz, u'c baz')
        request.form['field.foo'] = u'r foo'
        request.form['field.bar'] = u'r bar'
        request.form['field.a']   = u'r a'
        request.form['field.b']   = u'r b'
        request.form['field.baz'] = u'r baz'
        self.assertEqual(v.update(), '')
        self.assertEqual(c.foo, u'c foo')
        self.assertEqual(c.bar, u'c bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , u'c b')
        self.assertEqual(c.baz, u'c baz')
        self.failIf(getEvents())

    def test_update(self):
        c = C()
        request = TestRequest()
        v = EV(c, request)
        request.form[Update] = ''
        request.form['field.foo'] = u'r foo'
        request.form['field.bar'] = u'r bar'
        request.form['field.baz'] = u'r baz'
        request.form['field.a'] = u'c a'

        message = v.update()
        self.failUnless(message.startswith('Updated '), message)
        self.assertEqual(c.foo, u'r foo')
        self.assertEqual(c.bar, u'r bar')
        self.assertEqual(c.a  , u'c a')
        self.assertEqual(c.b  , None)
        self.assertEqual(c.baz, u'r baz')

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
