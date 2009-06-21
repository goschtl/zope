##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""

$Id:  2007-12-12 12:27:02Z fafhrd $
"""
import unittest, os
from zope.testing import doctest
from zope.app.testing.functional import ZCMLLayer, FunctionalDocFileSuite

layoutformLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'layoutformLayer', allow_teardown=True)


def test_suite():
    form = FunctionalDocFileSuite(
        "form.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    form.layer = layoutformLayer

    tests = FunctionalDocFileSuite(
        "tests.txt",
        optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    tests.layer = layoutformLayer

    return unittest.TestSuite((form, tests,))
