##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Tests of this package"""

import unittest

from zope.testing import doctest

flags = doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS

from zope.testing.cleanup import cleanUp

def setUp(test=None):
    cleanUp()

def tearDown(test=None):
    cleanUp()

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('mapply.txt', optionflags=flags),
        doctest.DocFileSuite('openroot.txt', optionflags=flags,
            setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('requestsetup.txt', optionflags=flags,
            setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('retry.txt', optionflags=flags),
    ])

if __name__ == '__main__':
    unittest.main()
