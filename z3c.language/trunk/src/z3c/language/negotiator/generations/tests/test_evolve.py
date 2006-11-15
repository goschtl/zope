##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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

import unittest
import zope.component
from zope.testing import doctest
from zope.testing import doctestunit
from zope.app.testing import setup

from z3c import testing

docTestPaths = ('../evolve1.txt',)


def test_suite():
    suites = []
    for filename in docTestPaths:
        suites.append(doctestunit.DocFileSuite(
            filename,
            setUp=testing.setUpGeneration, tearDown=testing.tearDownGeneration,
            globs = {'getDBRoot': testing.getDBRoot,
                     'getDB': testing.getDB},
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ))
    return unittest.TestSuite(suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
