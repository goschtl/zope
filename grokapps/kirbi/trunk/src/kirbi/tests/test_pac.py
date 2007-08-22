#!/usr/bin/env python

import unittest
from doctest import DocFileSuite

def test_suite():
    return unittest.TestSuite(DocFileSuite('test_pac.txt'))

if __name__ == '__main__':
    unittest.main()
