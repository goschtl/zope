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
$Id: testFormView.py,v 1.8 2002/07/17 16:54:15 jeremy Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Testing.CleanUp import CleanUp # Base class w registry cleanup

from Zope.ComponentArchitecture import getService
from Zope.ComponentArchitecture.tests.PlacelessSetup import PlacelessSetup

from Zope.Publisher.Browser.IBrowserView import IBrowserView
from Zope.App.Forms.Views.Browser.FormView import FormView

from Schema.IField import IStr
from Zope.App.Forms.Views.Browser.Widget import TextWidget, FileWidget

import SchemaTestObject


class TestFormView(TestCase, PlacelessSetup):
    def setUp(self):
        PlacelessSetup.setUp(self)
        viewService = self.getViewService()
        viewService.provideView(IStr, 'widget', IBrowserView, [TextWidget])
        request = SchemaTestObject.TestBrowserRequest(
            {'field_id': '1', 'field_title': 'Test New',
             'field_creator': 'srichter@cbu.edu', 'field_data': 'Data'})
        self._form = SchemaTestObject.EditFactory(request=request)
        
    def getViewService(self):
        return getService(None, 'Views')

    def testGetFields(self):
        fields = []
        schema = SchemaTestObject.STestObject
        for name in schema.names(1):
            fields.append(schema.getDescriptionFor(name))
        self.assertEqual(fields, self._form.getFields())


    def _compareWidgets(self, widget1, widget2):
        self.assertEqual(widget1.__class__, widget2.__class__)
        for prop in widget1.propertyNames:
            self.assertEqual(widget1.getValue(prop), widget2.getValue(prop))
        for prop in widget2.propertyNames:
            self.assertEqual(widget2.getValue(prop), widget1.getValue(prop))


    def testGetWidgetForField(self):
        field = SchemaTestObject.STestObject.getDescriptionFor('id')
        widget = TextWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForField(field)
        self._compareWidgets(widget, result)

        field = SchemaTestObject.STestObject.getDescriptionFor('data')
        widget = FileWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForField(field)
        self._compareWidgets(widget, result)


    def testGetWidgetForFieldId(self):
        field = SchemaTestObject.STestObject.getDescriptionFor('id')
        widget = TextWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForFieldId('id')
        self._compareWidgets(widget, result)

        field = SchemaTestObject.STestObject.getDescriptionFor('data')
        widget = FileWidget(field, SchemaTestObject.TestBrowserRequest({}))
        result = self._form.getWidgetForFieldId('data')
        self._compareWidgets(widget, result)

        self.assertRaises(KeyError, self._form.getWidgetForFieldId, 'foo')

    
    def testRenderField(self):
        field = SchemaTestObject.STestObject.getDescriptionFor('id')
        self.assertEqual(
            '<input name="field_id" type="text" value="1" size="20"  />',
            self._form.renderField(field))

        field = SchemaTestObject.STestObject.getDescriptionFor('creator')
        self.assertEqual('<input name="field_creator" type="text" '
                         'value="srichter@cbu.edu" size="30"  />',
                         self._form.renderField(field))


    def testGetAllRawFieldData(self):
        data = self._form.getAllRawFieldData()
        result = {'data': 'Data', 'id': '1', 'title': 'Test New',
                  'creator': 'srichter@cbu.edu'}
        for field in data.keys():
            self.assertEqual(result[field.id], data[field])


    def testConvertAllFieldData(self):
        data = self._form.getAllRawFieldData()
        data = self._form.convertAllFieldData(data)
        result = {'data': 'Data', 'id': 1, 'title': 'Test New',
                  'creator': 'srichter@cbu.edu'}
        for field in data.keys():
            self.assertEqual(result[field.id], data[field])


    def testValidateAllFieldData(self):
        data = self._form.getAllRawFieldData()
        data = self._form.convertAllFieldData(data)
        self.assertEqual(None, self._form.validateAllFieldData(data))


    def testStoreAllDataInContext(self):
        data = self._form.getAllRawFieldData()
        data = self._form.convertAllFieldData(data)
        self._form.storeAllDataInContext(data)
        obj = self._form.context
        for field in data.keys():
            self.assertEqual(data[field], getattr(obj, field.id))


    def testSaveValuesInContect(self):
        data = self._form.getAllRawFieldData()
        data = self._form.convertAllFieldData(data)
        self._form.saveValuesInContext()
        obj = self._form.context
        for field in data.keys():
            self.assertEqual(data[field], getattr(obj, field.id))


def test_suite():
    return makeSuite(TestFormView)

if __name__=='__main__':
    main(defaultTest='test_suite')
