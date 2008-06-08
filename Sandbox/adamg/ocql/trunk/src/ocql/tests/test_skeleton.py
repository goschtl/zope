# -*- coding: UTF-8 -*-

"""Main

$Id$
"""

import unittest

from ocql.engine import OCQLEngine
from ocql.testing.stubs import *

class testSkeleton(unittest.TestCase):
    def testSomething(self):
        registerStubs()

        e = OCQLEngine()
        rq = e.compile("[ c in ICurses | c ]")

        self.assert_(isinstance(rq, RunnableQuery))

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testSkeleton))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')