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
"""Pagelet tests

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest

import zope.component

from zope.security.checker import defineChecker

from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctestunit import DocFileSuite

from zope.app.testing import placelesssetup, ztapi, setup



def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.pagelet.tales'),
        DocTestSuite('zope.app.pagelet.collector'),
        DocFileSuite('../README.txt',
                     setUp=setup.placefulSetUp,
                     tearDown=setup.placefulTearDown(),
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
