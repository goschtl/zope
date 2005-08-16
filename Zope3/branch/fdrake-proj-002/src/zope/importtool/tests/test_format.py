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
"""Tests for zope.importtool.format.

$Id$
"""
import sys
import unittest

from StringIO import StringIO

from zope.importtool import format


class FormatTestCase(unittest.TestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        sys.stdout = self.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.old_stdout

    def test_two_column_report(self):
        format.two_column_report([("abc", "def"), ("abcdef", "ghijklm")])
        self.assertEqual(self.stdout.getvalue(),
                         "--------------\n"
                         "abc    def\n"
                         "abcdef ghijklm\n")


def test_suite():
    return unittest.makeSuite(FormatTestCase)
