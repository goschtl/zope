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

$Id: test_setfield.py,v 1.1 2004/04/24 23:19:23 srichter Exp $
"""
from unittest import TestSuite, main, makeSuite
from zope.schema import Set
from zope.schema.tests.test_tuplefield import TupleTest

# We could also choose the ListField as base test. It should not matter.
class SetTest(TupleTest):
    """Test the Set Field."""

    _Field_Factory = Set

def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(SetTest))
    return suite

if __name__ == '__main__':
    main(defaultTest='test_suite')
