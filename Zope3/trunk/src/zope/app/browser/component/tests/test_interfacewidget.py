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
"""Interface field widget tests

$Id: test_interfacewidget.py,v 1.22 2003/04/30 23:37:49 faassen Exp $
"""

__metaclass__ = type

from zope.interface import Interface
from unittest import TestCase, TestSuite, makeSuite
from zope.testing.cleanup import CleanUp
from zope.app.component.globalinterfaceservice import InterfaceService
from zope.app.component.globalinterfaceservice import IInterfaceService
from zope.app.component.interfacefield import InterfaceField, InterfacesField
from zope.app.browser.component.interfacewidget import InterfaceWidget
from zope.app.browser.component.interfacewidget import MultiInterfaceWidget
from zope.publisher.browser import TestRequest
from zope.component.service import serviceManager, defineService
from zope.app.services.servicenames import Interfaces
from zope.app.interfaces.form import ConversionError

class I(Interface):
    """bah blah
    """

class I2(Interface):
    """eek
    """

class I3(Interface):
    """
    """
    def one():
        """method one"""

    def two():
        """method two"""

class BaseInterfaceWidgetTest(CleanUp, TestCase):

    def setUp(self):
        service = InterfaceService()
        defineService(Interfaces, IInterfaceService)
        serviceManager.provideService(Interfaces, service)
        service.provideInterface(I.__module__+'.'+I.__name__, I)
        service.provideInterface(I2.__module__+'.'+I2.__name__, I2)
        service.provideInterface(I3.__module__+'.'+I3.__name__, I3)

        request = TestRequest()

        self.request = request


class TestInterfaceWidget(BaseInterfaceWidgetTest):

    def testInterfaceWidget(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = InterfaceWidget(field, request)

        self.assertEqual(widget.getData(), None)
        self.failIf(widget.haveData())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '" selected>'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget.getData(), None)
        self.failIf(widget.haveData())

        widget = InterfaceWidget(field, request)

        request.form["field.TestName"] = (
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getData(), I2)
        self.failUnless(widget.haveData())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '" selected>'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

        request.form["field.TestName.search"] = 'two'
        out = (
        '<input type="text" name="field.TestName.search" value="two">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

    def testInterfaceWidget_w_constraint(self):
        request = self.request
        field = InterfaceField(
            __name__='TestName',
            title=u"This is a test",
            required=False,
            constraint=lambda i: not (i.__name__.endswith("2")),
            )

        widget = InterfaceWidget(field, request)

        self.assertEqual(widget.getData(), None)
        self.failIf(widget.haveData())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

    def testInterfaceWidget_allow_None_as_well_as_interfaces(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               basetype=None)

        widget = InterfaceWidget(field, request)

        self.assertEqual(widget.getData(), None)
        self.failIf(widget.haveData())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'None'
        '">'
        'Anything'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

        request.form["field.TestName"] = (
        'None'
        )
        self.assertEqual(widget.getData(), None)
        self.failUnless(widget.haveData())

        out = (
        '<input type="text" name="field.TestName.search" value="">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'None'
        '" selected>'
        'Anything'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)

        # test that None / Anything disappears when there is a search string

        request.form["field.TestName.search"] = (
        'two'
        )

        out = (
        '<input type="text" name="field.TestName.search" value="two">'
        '<select name="field.TestName">'
        '<option value="">---select interface---</option>'

        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )

        self.assertEqual(widget(), out)


    def testBadInterfaceName(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = InterfaceWidget(field, request)

        request.form["field.TestName"] = ('bad interface name')
        self.assertRaises(ConversionError, widget.getData)

    def testHidden(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = InterfaceWidget(field, request)

        out = (
        '<input type="hidden" name="field.TestName" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)

        request.form["field.TestName"] = (
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getData(), I2)
        out = (
        '<input type="hidden" name="field.TestName"'
        ' value="zope.app.browser.component.tests.test_interfacewidget.I2" />'
        )
        self.assertEqual(widget.hidden(), out)

    def testHiddenNone(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               basetype=None)

        widget = InterfaceWidget(field, request)

        out = (
        '<input type="hidden" name="field.TestName" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)

        request.form["field.TestName"] = (
        'None'
        )
        self.assertEqual(widget.getData(), None)
        out = (
        '<input type="hidden" name="field.TestName" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)


# XXX Note that MultiInterface widgets should be for multi-interface fields

class TestMultiInterfaceWidget(BaseInterfaceWidgetTest):

    def testMultiInterfaceWidget(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u'This is a test',
                                required=False)
        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.getData(), ())
        self.failIf(widget.haveData())

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)
        self.failIf(widget.haveData())

        widget = MultiInterfaceWidget(field, request)

        request.form["field.TestName.i1"] = (
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getData(), (I2,))
        self.failUnless(widget.haveData())
        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'
        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'
        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '" selected>'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)
        self.failUnless(widget.haveData())

        # There is no selected option because the option that would be
        # selected has been filtered out by the search.
        request.form["field.TestName.search.i1"] = 'two'
        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="two">'

        '<select name="field.TestName.i1">'
        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)
        self.failUnless(widget.haveData())
        label = '<label for="field.TestName">This is a test</label>'
        self.assertEqual(widget.label(), label)
        self.assertEqual(widget.row(),
                         '<div class="label">%s</div>'
                         '<div class="field">%s</div>' % (label, out)
                         )

    def testMultiInterfaceWidgetNone(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u'This is a test',
                                basetype=None)
        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.getData(), ())
        self.failIf(widget.haveData())

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'Anything'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'Anything'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

        request.form["field.TestName.i1"] = 'None'
        self.assertEqual(widget.getData(), (None,))
        self.failUnless(widget.haveData())

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'Anything'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '" selected>'
        'Anything'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

        # test that None / Anything disappears when there is a search string

        request.form["field.TestName.search.i1"] = 'two'

        out = (
        'Use refresh to enter more interfaces'
        '<br />'

        '<input type="text" name="field.TestName.search.i0" value="">'

        '<select name="field.TestName.i0">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'None'
        '">'
        'Anything'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        '</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'

        '<br />'

        '<input type="text" name="field.TestName.search.i1" value="two">'

        '<select name="field.TestName.i1">'

        '<option value="">---select interface---</option>'
        '<option value="'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '">'
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        '</option>'

        '</select>'
        )
        self.assertEqual(widget(), out)

    def testBadInterfaceName(self):
        request = self.request
        field = InterfaceField(__name__='TestName',
                               title=u"This is a test",
                               required=False)

        widget = MultiInterfaceWidget(field, request)

        request.form["field.TestName.i0"] = ('bad interface name')
        self.assertRaises(ConversionError, widget.getData)

    def testHidden(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u"This is a test",
                                required=False)

        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.hidden(), '')

        request.form["field.TestName.i0"] = (
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        )
        self.assertEqual(widget.getData(), (I2,))
        out = (
        '<input type="hidden" name="field.TestName.i0"'
        ' value="zope.app.browser.component.tests.test_interfacewidget.I2" />'
        )
        self.assertEqual(widget.hidden(), out)

        request.form["field.TestName.i1"] = (
        'zope.app.browser.component.tests.test_interfacewidget.I3'
        )
        self.assertEqual(widget.getData(), (I2, I3))
        out = (
        '<input type="hidden" name="field.TestName.i0"'
        ' value="zope.app.browser.component.tests.test_interfacewidget.I2" />'
        '<input type="hidden" name="field.TestName.i1"'
        ' value="zope.app.browser.component.tests.test_interfacewidget.I3" />'
        )
        self.assertEqual(widget.hidden(), out)

    def testHiddenNone(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u"This is a test",
                                basetype=None)

        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.hidden(), '')

        request.form["field.TestName.i0"] = (
        'None'
        )
        self.assertEqual(widget.getData(), (None,))
        out = (
        '<input type="hidden" name="field.TestName.i0" value="None" />'
        )
        self.assertEqual(widget.hidden(), out)

    def testEmptyFormData(self):
        request = self.request
        field = InterfacesField(__name__='TestName',
                                title=u'This is a test',
                                required=False)
        widget = MultiInterfaceWidget(field, request)

        self.assertEqual(widget.getData(), ())
        self.failIf(widget.haveData())

        request.form["field.TestName.i1"] = (
        'zope.app.browser.component.tests.test_interfacewidget.I2'
        )
        request.form["field.TestName.i0"] = ''
        self.assertEqual(widget.getData(), (I2,))
        self.failUnless(widget.haveData())

class TestRenderInterfaceSelect(TestCase):

    def testInterfaceSelect(self):
        from zope.app.browser.component.interfacewidget \
            import renderInterfaceSelect
        interfaces = ['foo', 'bar', 'baz']
        selected = 'bar'
        search_name = 'searchname'
        search_string = 'foo"blee'
        select_name = 'selectname'
        out = (
        '''<input type="text" name="searchname" value=\'foo"blee\'>'''
        '''<select name="selectname">'''
        '''<option value="">---select interface---</option>'''
        '''<option value="foo">foo</option>'''
        '''<option value="bar" selected>bar</option>'''
        '''<option value="baz">baz</option>'''
        '''</select>'''
        )
        self.assertEqual(
            renderInterfaceSelect(interfaces, selected, search_name,
                                  search_string, select_name),
            out)

    def testEmptyInterfaceSelect(self):
        from zope.app.browser.component.interfacewidget \
            import renderInterfaceSelect
        interfaces = []
        selected = 'bar'
        search_name = 'searchname'
        search_string = 'fooblee'
        select_name = 'selectname'
        out = (
        '<input type="text" name="searchname" value="fooblee">'
        '<select name="selectname">'
        '<option value="">---select interface---</option>'
        '</select>'
        )
        self.assertEqual(
            renderInterfaceSelect(interfaces, selected, search_name,
                                  search_string, select_name),
            out)

def test_suite():
    return TestSuite((makeSuite(TestInterfaceWidget),
                      makeSuite(TestMultiInterfaceWidget),
                      makeSuite(TestRenderInterfaceSelect),
                    ))
