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
$Id: testDatetime.py,v 1.2 2002/11/11 20:24:35 jim Exp $
"""
from unittest import TestSuite, main, makeSuite
from Zope.Schema import Datetime, ErrorNames
from testField import FieldTestBase
from datetime import datetime

class DatetimeTest(FieldTestBase):
    """Test the Datetime Field."""

    _Field_Factory = Datetime

    def testValidate(self):
        field = Datetime(title=u'Datetime field', description=u'',
                        readonly=False, required=False)
        field.validate(None)
        field.validate(datetime.now())
        
    def testValidateRequired(self):
        field = Datetime(title=u'Datetime field', description=u'',
                    readonly=False, required=True)
        field.validate(datetime.now())
        
        self.assertRaisesErrorNames(ErrorNames.RequiredMissing,
                                    field.validate, None)

    def testAllowedValues(self):
        d1 = datetime(2000,10,1)
        d2 = datetime(2000,10,2)
        
        
        field = Datetime(title=u'Datetime field', description=u'',
                        readonly=False, required=False,
                         allowed_values=(d1, d2))
        field.validate(None)
        field.validate(d2)
        field.validate(datetime(2000,10,2))
    
        self.assertRaisesErrorNames(ErrorNames.InvalidValue,
                                    field.validate,
                                    datetime(2000,10,4))

    def testValidateMin(self):
        d1 = datetime(2000,10,1)
        d2 = datetime(2000,10,2)
        field = Datetime(title=u'Datetime field', description=u'',
                        readonly=False, required=False, min=d1)
        field.validate(None)
        field.validate(d1)
        field.validate(d2)
        field.validate(datetime.now())
        
        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate,
                                    datetime(2000,9,30))

    def testValidateMax(self):
        d1 = datetime(2000,10,1)
        d2 = datetime(2000,10,2)
        d3 = datetime(2000,10,3)
        field = Datetime(title=u'Datetime field', description=u'',
                        readonly=False, required=False, max=d2)
        field.validate(None)
        field.validate(d1)
        field.validate(d2)
    
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, d3)

    def testValidateMinAndMax(self):
        d1 = datetime(2000,10,1)
        d2 = datetime(2000,10,2)
        d3 = datetime(2000,10,3)
        d4 = datetime(2000,10,4)
        d5 = datetime(2000,10,5)

        field = Datetime(title=u'Datetime field', description=u'',
                        readonly=False, required=False, min=d2, max=d4)
        field.validate(None)
        field.validate(d2)
        field.validate(d3)
        field.validate(d4)

        self.assertRaisesErrorNames(ErrorNames.TooSmall, field.validate, d1)
        self.assertRaisesErrorNames(ErrorNames.TooBig, field.validate, d5)


def test_suite():
    return makeSuite(DatetimeTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
