##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""DottedName field tests
"""
from unittest import main, makeSuite

from six import b
from zope.schema import DottedName
from zope.schema.tests.test_field import FieldTestBase
from zope.schema.interfaces import InvalidDottedName, RequiredMissing

class DottedNameTest(FieldTestBase):
    """Test the DottedName Field."""

    _Field_Factory = DottedName

    def testValidate(self):
        field = self._Field_Factory(required=False)

        field.validate(None)
        field.validate(b('foo.bar'))
        field.validate(b('foo.bar0'))
        field.validate(b('foo0.bar'))
        
        # We used to incorrectly allow ^: https://bugs.launchpad.net/zope.schema/+bug/191236
        self.assertRaises(InvalidDottedName, field.validate, b('foo.bar^foobar'))
        self.assertRaises(InvalidDottedName, field.validate, b('foo^foobar.bar'))
        # dotted names cannot start with digits
        self.assertRaises(InvalidDottedName, field.validate, b('foo.0bar'))
        self.assertRaises(InvalidDottedName, field.validate, b('0foo.bar'))

    def testValidateRequired(self):
        field = self._Field_Factory(required=True)
        
        field.validate(b('foo.bar'))
        
        self.assertRaises(RequiredMissing, field.validate, None)

def test_suite():
    suite = makeSuite(DottedNameTest)
    return suite
