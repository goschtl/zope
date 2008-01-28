##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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

$Id$
"""
__docformat__ = 'restructuredtext'
import unittest
from zope.app.testing import functional
import os

zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')

functional.defineLayer('RemotetaskLayer', zcml)

def test_suite():
    suite1 = functional.FunctionalDocFileSuite('xmlrpc.txt')
    suite2 = functional.FunctionalDocFileSuite('browser/README.txt')
    suite1.layer = RemotetaskLayer
    suite2.layer = RemotetaskLayer
    return unittest.TestSuite((suite1, suite2))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
