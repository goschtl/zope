##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
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
"""Location support tests

$Id$
"""

import unittest
import zope.testing.doctest


def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite('location.txt'),
        zope.testing.doctest.DocTestSuite('zope.location.traversing'),
        zope.testing.doctest.DocTestSuite('zope.location.pickling'),
        ))
