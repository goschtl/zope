##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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

__docformat__ = "reStructuredText"

import doctest
import unittest
from zope.app.testing.placelesssetup import setUp
from zope.app.testing.placelesssetup import tearDown

from z3c.resource.resource import Resource
from z3c.resource.testing import BaseTestIResource


class TestResource(BaseTestIResource):

    def getTestClass(self):
        return Resource


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestResource),
        doctest.DocTestSuite('z3c.resource.resource'),
        doctest.DocTestSuite('z3c.resource.namespace'),
        doctest.DocFileSuite('README.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__': unittest.main()
