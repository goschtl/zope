##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Context Tests

$Id: tests.py 66343 2006-04-03 04:59:49Z philikon $
"""
import unittest
import doctest

def test_suite():
    suite = doctest.DocTestSuite()
    suite.addTest(doctest.DocTestSuite('zope.security.decorator'))
    return suite


if __name__ == '__main__':
    unittest.main()
