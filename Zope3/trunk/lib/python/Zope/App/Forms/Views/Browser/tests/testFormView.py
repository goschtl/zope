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
$Id: testFormView.py,v 1.16 2002/10/28 23:52:31 jim Exp $
"""
from cStringIO import StringIO
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

from Zope.ComponentArchitecture import getService
from Zope.App.tests.PlacelessSetup import PlacelessSetup

from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.App.Forms.Views.Browser.FormView import FormView

from Zope.Schema.IField import IBytes
from Zope.App.Forms.Views.Browser.Widget \
     import TextWidget, IntWidget, FileWidget

import SchemaTestObject


class TestFormView(TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)
        viewService = self.getViewService()
        viewService.provideView(IBytes, 'widget', IBrowserView, [TextWidget])
        request = SchemaTestObject.TestBrowserRequest(
            {'field.id': '1', 'field.title': 'Test New',
             'field.creator': 'srichter@cbu.edu',
             'field.data': StringIO('Data')})
        self._form = SchemaTestObject.EditFactory(request=request)
        self.__data = {'id': 1,
                       'title': 'Test New',
                       'creator': 'srichter@cbu.edu',
                       'data': 'Data'}
        
    def getViewService(self):
        return getService(None, 'Views')

    def testGetFields(self):
        fields = []
        schema = SchemaTestObject.ITestObject
        for name in schema.names(1):
            fields.append(schema.getDescriptionFor(name))
        fields.sort()

        result = self._form.getFields()
        result.sort()

        self.assertEqual(fields, result)


    def _compareWidgets(self, widget1, widget2):
        self.assertEqual(widget1.__class__, widget2.__class__)
        for prop in widget1.propertyNames:
            self.assertEqual(widget1.getValue(prop), widget2.getValue(prop))
        for prop in widget2.propertyNames:
            self.assertEqual(widget2.getValue(prop), widget1.getValue(prop))


    def testGetWidgetForField(self):
        field = SchemaTestObject.ITestObject.getDescriptionFor('id')
        widget = IntWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForField(field)
        self._compareWidgets(widget, result)

        field = SchemaTestObject.ITestObject.getDescriptionFor('data')
        widget = FileWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForField(field)
        self._compareWidgets(widget, result)


    def testGetWidgetForFieldName(self):
        field = SchemaTestObject.ITestObject.getDescriptionFor('id')
        widget = IntWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForFieldName('id')
        self._compareWidgets(widget, result)

        field = SchemaTestObject.ITestObject.getDescriptionFor('data')
        widget = FileWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForFieldName('data')
        self._compareWidgets(widget, result)

        self.assertRaises(KeyError, self._form.getWidgetForFieldName, 'foo')

    
    def testRenderField(self):
        field = SchemaTestObject.ITestObject.getDescriptionFor('id')
        self.assertEqual(
            '<input name="field.id" type="text" value="5" size="10"  />',
            self._form.renderField(field))

        field = SchemaTestObject.ITestObject.getDescriptionFor('creator')
        self.assertEqual('<input name="field.creator" type="text" '
                         'value="strichter@yahoo.com" size="30"  />',
                         self._form.renderField(field))


    def testSaveValuesInContext(self):
        data = self.__data
        self._form.saveValuesInContext()
        obj = self._form.context
        for name, value in data.iteritems():
            self.assertEqual(value, getattr(obj, name))

def test_suite():
    return makeSuite(TestFormView)

if __name__=='__main__':
    main(defaultTest='test_suite')
