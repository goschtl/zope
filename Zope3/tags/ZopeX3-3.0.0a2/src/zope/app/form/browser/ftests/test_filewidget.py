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

$Id$
"""

import unittest
from StringIO import StringIO
from persistent import Persistent
from transaction import get_transaction

from zope.interface import Interface
from zope.interface import implements

from zope.schema.interfaces import IField
from zope.schema import Field

from zope.app.form.browser.textwidgets import FileWidget

from support import *
from zope.app.traversing.api import traverse

from zope.app.tests.functional import BrowserTestCase
from zope.app.form.interfaces import IInputWidget

class IFileField(IField):
    """Field for representing a file that can be edited by FileWidget."""


class FileField(Field):

    implements(IFileField)


defineWidgetView(IFileField, FileWidget, IInputWidget)


class IFileTest(Interface):

    f1 = FileField()
    f2 = FileField(required=False)

registerEditForm(IFileTest)


class FileTest(Persistent):

    implements(IFileTest)

    def __init__(self):
        self.f1 = None
        self.f2 = 'foo'

defineSecurity(FileTest, IFileTest)


class SampleTextFile(StringIO):

    def __init__(self, buf, filename=''):
        StringIO.__init__(self, buf)
        self.filename = filename


class Test(BrowserTestCase):

    sampleText = "The quick brown fox\njumped over the lazy dog."
    sampleTextFile = SampleTextFile(sampleText)

    emptyFileName = 'empty.txt'
    emptyFile = SampleTextFile('', emptyFileName)


    def test_display_editform(self):
        self.getRootFolder()['test'] = FileTest()
        get_transaction().commit()

        # display edit view
        response = self.publish('/test/edit.html')
        self.assertEqual(response.getStatus(), 200)

        # field should be displayed in a file input element
        self.assert_(patternExists(
            '<input .* name="field.f1".* type="file".*>', response.getBody()))
        self.assert_(patternExists(
            '<input .* name="field.f2".* type="file".*>', response.getBody()))


    def test_submit_text(self):
        self.getRootFolder()['test'] = FileTest()
        get_transaction().commit()
        object = traverse(self.getRootFolder(), 'test')
        self.assert_(object.f1 is None)
        self.assertEqual(object.f2, 'foo')

        # submit a sample text file
        response = self.publish('/test/edit.html', form={
            'UPDATE_SUBMIT' : '',
            'field.f1' : self.sampleTextFile,
            'field.f2' : self.sampleTextFile })
        self.assertEqual(response.getStatus(), 200)
        self.assert_(updatedMsgExists(response.getBody()))

        # check new values in object
        object = traverse(self.getRootFolder(), 'test')
        object._p_jar.sync()
        self.assertEqual(object.f1, self.sampleText)
        self.assertEqual(object.f2, self.sampleText)


    def XXX_test_invalid_value(self):
        self.getRootFolder()['test'] = FileTest()
        get_transaction().commit()

        # submit an invalid file value
        response = self.publish('/test/edit.html', form={
            'UPDATE_SUBMIT' : '',
            'field.f1' : 'not a file' })
        self.assertEqual(response.getStatus(), 200)

        print response.getBody()

        self.assert_(validationErrorExists('f1',
            'Value is not a file object', response.getBody()))


    def XXX_test_required_validation(self):
        self.getRootFolder()['test'] = TextLineTest()
        get_transaction().commit()

        # submit missing values for required field s1
        response = self.publish('/test/edit.html', form={
            'UPDATE_SUBMIT' : '',
            'field.f1' : sampleTextFile,
            'field.f2' : '' })
        self.assertEqual(response.getStatus(), 200)

        # confirm error msgs
        self.assert_(missingInputErrorExists('s1', response.getBody()))
        self.assert_(not missingInputErrorExists('s2', response.getBody()))


    def test_empty_file(self):
        self.getRootFolder()['test'] = FileTest()
        get_transaction().commit()

        # submit an empty text file
        response = self.publish('/test/edit.html', form={
            'UPDATE_SUBMIT' : '',
            'field.f2' : self.emptyFile })
        self.assertEqual(response.getStatus(), 200)
        self.assert_(updatedMsgExists(response.getBody()))

        # new value for f1 should be field.missing_value (i.e, None)
        object = traverse(self.getRootFolder(), 'test')
        object._p_jar.sync()
        self.assert_(object.f1 is None)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')


