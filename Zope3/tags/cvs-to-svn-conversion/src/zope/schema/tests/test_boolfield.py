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
$Id: test_boolfield.py,v 1.4 2004/04/11 10:35:17 srichter Exp $
"""
from unittest import main, makeSuite
from zope.schema import Bool
from zope.schema.interfaces import RequiredMissing
from zope.schema.tests.test_field import FieldTestBase

class BoolTest(FieldTestBase):
    """Test the Bool Field."""

    _Field_Factory = Bool

    def testValidate(self):
        field = Bool(title=u'Bool field', description=u'',
                     readonly=False, required=False)
        field.validate(None)
        field.validate(True)
        field.validate(False)

    def testValidateRequired(self):
        field = Bool(title=u'Bool field', description=u'',
                     readonly=False, required=True)
        field.validate(True)
        field.validate(False)

        self.assertRaises(RequiredMissing, field.validate, None)


def test_suite():
    return makeSuite(BoolTest)

if __name__ == '__main__':
    main(defaultTest='test_suite')
