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
"""ComponentPathWidget tests.

$Id: test_field_widget.py,v 1.13 2003/06/30 16:23:33 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.interface import Interface, implements
from zope.publisher.browser import TestRequest

class FakeComponentPath:

    default = None

    def __init__(self, context, type):
        self.context = context
        self.type = type

    def validate(self, value):
        pass

    __name__ = 'X'
    title = 'fake component field'
    required = True

class I1(Interface):  pass

class I2(Interface):  pass

class C:
    implements(I1)

class D:
    implements(I2)

instanceOfComponentC = C()

class BaseTest(PlacefulSetup, TestCase):

    def createWidget(self, field, request):
        from zope.app.browser.services.field import ComponentPathWidget
        return ComponentPathWidget(field, request)

    def setUp(self):
        PlacefulSetup.setUp(self, site=True)
        default = traverse(self.rootFolder, '++etc++site/default')
        default.setObject('c1', C())
        default.setObject('c2', C())
        default.setObject('c3', C())
        default.setObject('d1', D())
        default.setObject('d2', D())
        default.setObject('d3', D())

        self.request = TestRequest()
        self.defaultpackage = default


class TestComponentPathWidget(BaseTest):

    def test(self):
        fake = FakeComponentPath(self.defaultpackage, I1)
        widget = self.createWidget(fake, self.request)

        expected = (
            '<select name="field.X">'
            '<option></option>'
            '<option>/++etc++site/default/c1</option>'
            '<option>/++etc++site/default/c2</option>'
            '<option>/++etc++site/default/c3</option>'
            '</select>'
            )

        self.assertEqual(widget(), expected)

        self.request.form['field.X'] = u'/++etc++site/default/c2'

        expected = (
            '<select name="field.X">'
            '<option></option>'
            '<option>/++etc++site/default/c1</option>'
            '<option selected>/++etc++site/default/c2</option>'
            '<option>/++etc++site/default/c3</option>'
            '</select>'
            )

        self.assertEqual(widget(), expected)

    def test_convert(self):
        fake = FakeComponentPath(None, I1)
        widget = self.createWidget(fake, self.request)
        self.assertEqual(widget._convert(u''), None)
        self.assertEqual(widget._convert(u'/a'), u'/a')

    def test_haveData(self):

        # Empty string means we don't have data
        fake = FakeComponentPath(None, I1)
        self.request.form['field.X'] = ''
        widget = self.createWidget(fake, self.request)
        self.failIf(widget.haveData())

        self.request.form['field.X'] = '/foo'
        widget = self.createWidget(fake, self.request)
        self.failUnless(widget.haveData())

        self.request.form['field.X'] = None
        widget = self.createWidget(fake, self.request)
        self.failIf(widget.haveData())


def test_suite():
    return TestSuite((
        makeSuite(TestComponentPathWidget),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
