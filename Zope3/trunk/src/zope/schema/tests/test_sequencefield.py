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
"""Sequence and Tuple field tests.

This set of tests exercises both Tuple and Sequence.  The only
behavior Tuple adds to sequence is the restriction of the type
to 'tuple'.

$Id: test_sequencefield.py,v 1.1 2004/04/24 23:19:23 srichter Exp $
"""
from unittest import TestSuite, main, makeSuite

from zope.interface import implements
from zope.schema import Sequence
from zope.schema.interfaces import NotAContainer, RequiredMissing
from zope.schema.tests.test_field import FieldTestBase

class SequenceTest(FieldTestBase):
    """Test the Sequence Field."""

    _Field_Factory = Sequence

    def testValidate(self):
        field = self._Field_Factory(title=u'test field', description=u'',
                                    readonly=False, required=False)
        field.validate(None)
        field.validate(())
        field.validate([])
        field.validate('')
        field.validate({})
        field.validate([1, 2])

        self.assertRaises(NotAContainer, field.validate, 1)

    def testValidateRequired(self):
        field = self._Field_Factory(title=u'test field', description=u'',
                                    readonly=False, required=True)
        field.validate([1, 2])

        self.assertRaises(RequiredMissing, field.validate, None)

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SequenceTest))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
