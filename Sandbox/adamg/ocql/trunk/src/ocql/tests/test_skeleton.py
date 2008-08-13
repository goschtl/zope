# -*- coding: UTF-8 -*-

"""Main

$Id$
"""

import unittest
import doctest
from zope.testing.doctestunit import DocTestSuite,DocFileSuite

from ocql.engine import OCQLEngine
from ocql.testing.stubs import *

from ocql.testing import utils

class testSkeleton(unittest.TestCase):
    def testSomething(self):
        registerStubs()

        e = OCQLEngine()
        rq = e.compile("[ c in ICourse | c ]")

        self.assert_(isinstance(rq, RunnableQuery))

def test_suite():
    flags =  doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
    return unittest.TestSuite((
        unittest.makeSuite(testSkeleton),
        DocFileSuite('run.txt',
                     optionflags=flags,
                     setUp = utils.setupAdapters),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')