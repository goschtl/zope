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

$Id: testSchema.py,v 1.2 2002/06/25 10:21:01 perry Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Schema.Exceptions import StopValidation, ValidationError, ValidationErrorsAll
from Schema._Schema import validateMapping,validateMappingAll
from Interface import Interface
import Schema

class ISchemaTest(Interface):
    title = Schema.Str(
                      title="Title"
		      ,description="Title"
		      ,default=""
		      ,required=1
		      )
    description = Schema.Str(
                      title="Description"
		      ,description="Description"
		      ,default=""
		      ,required=1
		      )
    spam = Schema.Str(
                      title="Spam"
		      ,description="Spam"
		      ,default=""
		      ,required=1
		      )
    
class SchemaTestCase(TestCase):
    def test_validateMapping(self):
        dict = {
	        'title': 'A title',
		'description': 'A particular description.',
		'spam': 'Spam',
                }
	try:
	    validateMapping(ISchemaTest, dict)
	except ValidationError:
	    self.fail()
	     

    def test_validateBadMapping(self):
        dict = {'title': 'A title'
		}
	
	self.assertRaises(ValidationError, validateMapping, ISchemaTest, dict)

    def test_validateMappingAll(self):
        dict = {
	        'title': 'A title',
		'description': 'A particular description.',
		'spam': 'Spam',
                }
	try:
	    validateMappingAll(ISchemaTest, dict)
	except ValidationErrorsAll:
	    self.fail()
	     

    def test_validateBadMappingAll(self):
        dict = {'title': 'A title'
		}
	
	try:
	    validateMappingAll(ISchemaTest, dict)
	except ValidationErrorsAll, e:
	    error=ValidationError("Must be required")
	    self.assertEqual(e.errors , [('description',error),
	                                 ('spam',error)]
			    )
	self.assertRaises(ValidationError, validateMapping, ISchemaTest, dict)

def test_suite():
    return TestSuite((
        makeSuite(SchemaTestCase),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
