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
$Id: testSchema.py,v 1.2 2002/09/07 16:18:51 jim Exp $
"""
from unittest import TestCase, TestSuite, main, makeSuite
from Zope.Schema.Exceptions import StopValidation, ValidationError, \
     ValidationErrorsAll
from Interface import Interface
from Zope.Schema import Bytes, ErrorNames
from Zope.Schema import validateMapping, validateMappingAll, getFields

class ISchemaTest(Interface):
    title = Bytes(
        title="Title",
        description="Title",
        default="",
        required=1)
    
    description = Bytes(
        title="Description",
        description="Description",
        default="",
        required=1)

    spam = Bytes(
        title="Spam",
        description="Spam",
        default="",
        required=1)

class SchemaTest(TestCase):

    def testValidateMapping(self):
        dict = {'title': 'A title',
                'description': 'A particular description.',
                'spam': 'Spam'}
        try:
            validateMapping(ISchemaTest, dict)
        except ValidationError, e:
            self.fail("Unexpected ValidationError: %s" % e.error_name)

    def testValidateBadMapping(self):
        dict = {'title': 'A title'}
        self.assertRaises(ValidationError, validateMapping, ISchemaTest, dict)

    def testValidateMappingAll(self):
        dict = {'title': 'A title',
                'description': 'A particular description.',
                'spam': 'Spam',
                }
        try:
            validateMappingAll(ISchemaTest, dict)
        except ValidationErrorsAll:
            self.fail("Unexpected ValidationErrors")

    def test_validateBadMappingAll(self):
        dict = {'title': 'A title'}
        try:
            validateMappingAll(ISchemaTest, dict)
        except ValidationErrorsAll, e:
            error=ValidationError(ErrorNames.RequiredMissing)
            self.assertEqual(e.errors ,
                             [('description',error), ('spam',error)])
            self.assertRaises(ValidationError, validateMapping, ISchemaTest,
                              dict)
            return
        self.fail('Expected ValidationErrors, but none detected')

    def test_getFields(self):
        fields = getFields(ISchemaTest)

        self.assert_(fields.has_key('title'))
        self.assert_(fields.has_key('description'))
        self.assert_(fields.has_key('spam'))

        # test whether getName() has the right value
        for key, value in fields.iteritems():
            self.assertEquals(key, value.getName())
        

def test_suite():
    return makeSuite(SchemaTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
