##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for zope.dependencytool.finddeps.

$Id$
"""
import unittest

from zope.dependencytool import finddeps


class HelperFunctionTestCase(unittest.TestCase):

    def test_makeDottedName(self):
        self.assertEqual(finddeps.makeDottedName(__file__), __name__)


def test_suite():
    return unittest.makeSuite(HelperFunctionTestCase)
