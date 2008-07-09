# -*- coding: UTF-8 -*-

"""Main

$Id$
"""

import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from ocql.testing.utils import *

class testUtils(unittest.TestCase):
    def testCatalog(self):
        setupInterfaces(None)
        setupCatalog(None)
        queryCatalog()


def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(testUtils),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')