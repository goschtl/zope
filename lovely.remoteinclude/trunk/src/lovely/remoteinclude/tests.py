##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
from zope.app.testing import setup
from z3c.testing import layer

layer.defineLayer('RemoteIncludeLayer', zcml='ftesting.zcml', clean=True)

def test_suite():
    fsuite = functional.FunctionalDocFileSuite('README.txt')
    fsuite.layer=RemoteIncludeLayer
    level2Suites = (
        fsuite,
        )
    for suite in level2Suites:
        suite.level = 2
    return unittest.TestSuite(level2Suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
