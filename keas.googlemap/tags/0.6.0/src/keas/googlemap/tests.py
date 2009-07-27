##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Test Setup.

$Id$
"""
import unittest
import zope.testing.doctest
from zope.app.testing import placelesssetup

from keas.googlemap import testing

def setUp(test):
    placelesssetup.setUp(test)
    testing.setUpGoogleMap()

def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite('README.txt',
                                          setUp=setUp,
                                          tearDown=placelesssetup.tearDown,
                                          optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                                          zope.testing.doctest.ELLIPSIS),
        ))
