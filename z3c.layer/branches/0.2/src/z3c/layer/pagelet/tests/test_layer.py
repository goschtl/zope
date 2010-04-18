##############################################################################
#
# Copyright (c) 2007-2010 Zope Foundation and Contributors.
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
"""
$Id: test_layer.py 111023 2010-04-17 23:31:18Z ccomb $
"""
import re
import unittest
from zope.testing import renormalizing
from zope.app.testing import functional


functional.defineLayer('TestLayer', 'ftesting.zcml')


checker = renormalizing.RENormalizing([
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:'),
    ])


def create_suite(*args, **kw):
    suite = functional.FunctionalDocFileSuite(*args, **kw)
    suite.layer = TestLayer
    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(create_suite('../README.txt', checker=checker))
    suite.addTest(create_suite('bugfixes.txt'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

