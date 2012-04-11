##############################################################################
#
# Copyright (c) 2012 Zope Foundation and Contributors.
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
import unittest

import six

from zope.schema import Text, Bytes, NativeString
from zope.schema import TextLine, BytesLine, NativeStringLine

class TestNativeString(unittest.TestCase):

    def test_string_py2(self):
        if six.PY3:
            return
        self.assertTrue(NativeString is Bytes)
        self.assertTrue(NativeStringLine is BytesLine)

    def test_string_py3(self):
        if not six.PY3:
            return
        self.assertTrue(NativeString is Text)
        self.assertTrue(NativeStringLine is TextLine)

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestNativeString))
    return suite
