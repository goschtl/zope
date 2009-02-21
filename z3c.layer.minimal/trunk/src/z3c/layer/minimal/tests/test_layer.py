##############################################################################
#
# Copyright (c) 2005-2009 Zope Foundation and Contributors.
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
$Id: test_layer.py 73898 2007-03-29 09:10:19Z shh $
"""

import unittest
from zope.app.testing import functional


functional.defineLayer('TestLayer', 'ftesting.zcml')


def create_suite(*args, **kw):
    suite = functional.FunctionalDocFileSuite(*args, **kw)
    suite.layer = TestLayer
    return suite


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(create_suite('../README.txt'))
    suite.addTest(create_suite('bugfixes.txt'))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
