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

$Id: test_field_widget.py,v 1.7 2003/03/23 22:35:36 jim Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite
from zope.app.services.tests.placefulsetup import PlacefulSetup
from zope.app.traversing import traverse
from zope.interface import Interface
from zope.app.services.service import ServiceManager
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
    __implements__ = I1

class D:
    __implements__ = I2

instanceOfComponentC = C()

class BaseTest(PlacefulSetup, TestCase):

    def createWidget(self, field, request):
        from zope.app.browser.services.field import ComponentPathWidget
        return ComponentPathWidget(field, request)

    def setUp(self):
        PlacefulSetup.setUp(self)
        self.buildFolders()
        self.rootFolder.setServiceManager(ServiceManager())
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


class TestComponentLocationWidget(BaseTest):

    def createWidget(self, field, request):
        from zope.app.browser.services.field import ComponentLocationWidget
        return ComponentLocationWidget(field, request)

    def test(self):
        fake = FakeComponentPath(self.defaultpackage, I1)
        widget = self.createWidget(fake, self.request)

        expected = (
            'path: '
            '<select name="field.X.p">'
            '<option></option>'
            '<option>/++etc++site/default/c1</option>'
            '<option>/++etc++site/default/c2</option>'
            '<option>/++etc++site/default/c3</option>'
            '</select>'
            '<br>'
            'dotted name: '
            '<input type="text" name="field.X.d" value="">'
            )

        self.assertEqual(widget(), expected)
        self.failIf(widget.haveData())
        self.assertEqual(widget.hidden(), '')

        self.request.form['field.X.p'] = (
                u'/++etc++site/default/c2')

        expected = (
            'path: '
            '<select name="field.X.p">'
            '<option></option>'
            '<option>/++etc++site/default/c1</option>'
            '<option selected>/++etc++site/default/c2</option>'
            '<option>/++etc++site/default/c3</option>'
            '</select>'
            '<br>'
            'dotted name: '
            '<input type="text" name="field.X.d" value="">'
            )

        self.assertEqual(widget(), expected)
        self.failUnless(widget.haveData())
        self.assertEqual(widget.hidden(),
                         '<input type="hidden" name="field.X.p" value="'
                         '/++etc++site/default/c2'
                         '" />'
                         )

        self.request.form['field.X.d'] = (
                u'zope.app.browser.services.tests.test_field_widget'
                u'.instanceOfComponentC')
        self.failIf(widget.haveData())

        from zope.app.interfaces.form import WidgetInputError
        self.assertRaises(WidgetInputError, widget.hidden)

        del self.request.form['field.X.p']
        self.failUnless(widget.haveData())

        expected = (
            'path: '
            '<select name="field.X.p">'
            '<option></option>'
            '<option>/++etc++site/default/c1</option>'
            '<option>/++etc++site/default/c2</option>'
            '<option>/++etc++site/default/c3</option>'
            '</select>'
            '<br>'
            'dotted name: '
            '<input type="text" name="field.X.d" value="'
            'zope.app.browser.services.tests.test_field_widget'
            '.instanceOfComponentC'
            '">'
            )
        self.assertEqual(widget(), expected)
        self.assertEqual(widget.hidden(),
                         '<input type="hidden" name="field.X.d" value="'
                         'zope.app.browser.services.tests.test_field_widget'
                         '.instanceOfComponentC'
                         '" />'
                         )

def test_suite():
    return TestSuite((
        makeSuite(TestComponentPathWidget),
        makeSuite(TestComponentLocationWidget),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
