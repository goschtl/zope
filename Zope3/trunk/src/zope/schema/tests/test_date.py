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
$Id: test_date.py,v 1.2 2004/01/16 13:38:20 philikon Exp $
"""
from unittest import main, makeSuite
from zope.schema import Date, EnumeratedDate
from zope.schema import errornames
from zope.schema.tests.test_field import FieldTestBase
from datetime import datetime, date

class DateTest(FieldTestBase):
    """Test the Date Field."""

    _Field_Factory = Date

    def testValidate(self):
        field = self._Field_Factory(title=u'Date field', description=u'',
                                    readonly=False, required=False)
        field.validate(None)
        field.validate(datetime.now().date())

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'Date field', description=u'',
                                    readonly=False, required=True)
        field.validate(datetime.now().date())

        self.assertRaisesErrorNames(errornames.RequiredMissing,
                                    field.validate, None)

    def testValidateMin(self):
        d1 = date(2000,10,1)
        d2 = date(2000,10,2)
        field = self._Field_Factory(title=u'Date field', description=u'',
                                    readonly=False, required=False, min=d1)
        field.validate(None)
        field.validate(d1)
        field.validate(d2)
        field.validate(datetime.now().date())

        self.assertRaisesErrorNames(errornames.TooSmall, field.validate,
                                    date(2000,9,30))

    def testValidateMax(self):
        d1 = date(2000,10,1)
        d2 = date(2000,10,2)
        d3 = date(2000,10,3)
        field = self._Field_Factory(title=u'Date field', description=u'',
                                    readonly=False, required=False, max=d2)
        field.validate(None)
        field.validate(d1)
        field.validate(d2)

        self.assertRaisesErrorNames(errornames.TooBig, field.validate, d3)

    def testValidateMinAndMax(self):
        d1 = date(2000,10,1)
        d2 = date(2000,10,2)
        d3 = date(2000,10,3)
        d4 = date(2000,10,4)
        d5 = date(2000,10,5)

        field = self._Field_Factory(title=u'Date field', description=u'',
                                    readonly=False, required=False,
                                    min=d2, max=d4)
        field.validate(None)
        field.validate(d2)
        field.validate(d3)
        field.validate(d4)

        self.assertRaisesErrorNames(errornames.TooSmall, field.validate, d1)
        self.assertRaisesErrorNames(errornames.TooBig, field.validate, d5)

class EnumeratedDateTest(DateTest):
    """Test the EnumeratedDate Field."""

    _Field_Factory = EnumeratedDate

    def testAllowedValues(self):
        d1 = date(2000,10,1)
        d2 = date(2000,10,2)

        field = self._Field_Factory(title=u'Date field', description=u'',
                                    readonly=False, required=False,
                                    allowed_values=(d1, d2))
        field.validate(None)
        field.validate(d2)
        field.validate(date(2000,10,2))

        self.assertRaisesErrorNames(errornames.InvalidValue,
                                    field.validate,
                                    date(2000,10,4))


def test_suite():
    suite = makeSuite(DateTest)
    suite.addTest(makeSuite(EnumeratedDateTest))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
