##############################################################################
#
# Copyright (c) 2008 Vanguardistas and Contributors.
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
import doctest

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite('van.pydeb'))
    suite.addTest(doctest.DocFileSuite('translations.txt'))
    suite.addTest(doctest.DocFileSuite('extras.txt'))
    suite.addTest(doctest.DocFileSuite('version.txt'))
    return suite
