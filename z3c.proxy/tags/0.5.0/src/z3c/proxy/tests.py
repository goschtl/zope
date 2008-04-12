###############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.testing.doctestunit import DocFileSuite
from zope.app.container.sample import SampleContainer
from zope.app.testing.placelesssetup import setUp
from zope.app.testing.placelesssetup import tearDown

from z3c.proxy import testing


class SampleContainerTest(testing.BaseTestIContainerLocationProxy):
    """Base container test sample."""

    def getTestInterface(self):
        return testing.ISampleContainerProxy

    def getTestClass(self):
        return testing.SampleContainerProxy 

    def makeTestObject(self):
        obj = SampleContainer()
        return testing.SampleContainerProxy(obj)


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp, tearDown=tearDown),
        unittest.makeSuite(SampleContainerTest),
        ))

if __name__ == '__main__': unittest.main(SampleContainerTest)
