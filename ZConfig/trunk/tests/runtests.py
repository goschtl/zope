#! /usr/bin/env python
"""Script to run all the regression tests for the ZConfig package."""

import os
import sys
import unittest

if __name__ == "__main__":
    __file__ = sys.argv[0]

TESTDIR = os.path.dirname(os.path.abspath(__file__))

TOPDIR = os.path.dirname(os.path.dirname(TESTDIR))

if TOPDIR not in sys.path:
    sys.path.append(TOPDIR)

def load_tests(name):
    name = "ZConfig.tests." + name
    __import__(name)
    mod = sys.modules[name]
    return mod.test_suite()

def test_suite():
    L = []
    for fn in os.listdir(TESTDIR):
        name, ext = os.path.splitext(fn)
        if name[:4] == "test" and ext == ".py":
            L.append(load_tests(name))
    if len(L) == 1:
        return L[0]
    else:
        suite = unittest.TestSuite()
        for t in L:
            suite.addTest(t)
        return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
