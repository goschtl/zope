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

$Id: testSchema.py,v 1.1 2002/06/24 08:31:48 faassen Exp $
"""

from unittest import TestCase, TestSuite, main, makeSuite

from Schema.Exceptions import StopValidation, ValidationError
from Schema._Schema import validate
from Schema.IField import IStr
        
class SchemaTestCase(TestCase):
    def test_validate(self):
        dict = {'title': 'A title',
                'description': 'A particular description.',
                'readonly': 0}
        
        result = validate(IStr, dict)
        for key, value in dict.items():
            self.assertEquals(value, result[key]) 
        
def test_suite():
    return TestSuite((
        makeSuite(SchemaTestCase),
        ))

if __name__ == '__main__':
    main(defaultTest='test_suite')
