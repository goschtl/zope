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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: test_widget.py,v 1.3 2003/01/09 14:13:10 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.form.widget import Widget, CustomWidget
from zope.app.interfaces.form import IWidget
from zope.interface.verify import verifyObject
from zope.schema import Text
from zope.publisher.browser import TestRequest
from zope.component.interfaces import IViewFactory

class TestWidget(TestCase):

    def test_name(self):
        w = Widget(Text(__name__='foo', title=u'Foo title'), TestRequest())
        self.assertEqual(w.name, 'field.foo')

    def test_setPrefix(self):
        w = Widget(Text(__name__='foo', title=u'Foo title'), TestRequest())
        w.setPrefix('test')
        self.assertEqual(w.name, 'test.foo')

    def test_title(self):
        w = Widget(Text(__name__='foo', title=u'Foo title'), TestRequest())
        self.assertEqual(w.title, 'Foo title')

    def test_IWidget(self):
        w = Widget(Text(__name__='foo', title=u'Foo title'), TestRequest())
        verifyObject(IWidget, w)

    # XXX Don't test getValue. It's silly and will go away.

class TestCustomWidget(TestCase):

    # XXX this test should be rewritten once we've refactored widget properties

    def test(self):
        cw = CustomWidget(Widget, width=60)
        verifyObject(IViewFactory, cw)
        w = cw(Text(__name__='foo', title=u'Foo title'), TestRequest())
        self.assertEqual(w.name, 'field.foo')
        self.assertEqual(w.width, 60)
        verifyObject(IWidget, w)



def test_suite():
    return TestSuite((
        makeSuite(TestWidget),
        makeSuite(TestCustomWidget),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
