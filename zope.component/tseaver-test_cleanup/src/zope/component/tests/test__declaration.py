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
"""Test adapter declaration helpers
"""
import unittest

class Test_adapts(unittest.TestCase):

    def test_instances_not_affected(self):
        from zope.component._declaration import adapts
        class C(object):
            adapts()

        self.assertEqual(C.__component_adapts__, ())
        def _try():
            return C().__component_adapts__
        self.assertRaises(AttributeError, _try)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test_adapts),
    ))
