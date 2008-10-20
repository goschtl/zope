#############################################################################
#
# Copyright (c) 2003, 2004,2005 Zope Corporation and Contributors.
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
"""Functional Tests for z3c.boston.Boston skin.

$Id$
"""
import unittest

from zope.testing import doctest
from zope.app.testing.functional import FunctionalDocFileSuite
from z3c.boston.testing import BostonLayer

def test_suite():
    boston_doctest = FunctionalDocFileSuite(
        "README.txt",
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)
    boston_doctest.layer = BostonLayer
    return unittest.TestSuite((
        boston_doctest,
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
