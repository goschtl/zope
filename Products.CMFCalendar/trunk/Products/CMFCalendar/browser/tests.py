##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Unit tests for browser module.
"""

import unittest
from Testing import ZopeTestCase

from Products.CMFCalendar.testing import FunctionalLayer


def test_suite():
    suite = unittest.TestSuite()
    s = ZopeTestCase.FunctionalDocFileSuite('event.txt')
    s.layer = FunctionalLayer
    suite.addTest(s)
    return suite
