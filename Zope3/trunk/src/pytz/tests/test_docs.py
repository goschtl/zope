#!/usr/bin/env python
# -*- coding: ascii -*-

import unittest, os, os.path, sys
from doctest import DocFileSuite
sys.path.insert(0, os.path.join(os.pardir, os.pardir))

README = DocFileSuite('../README.txt')

def test_suite():
    return README

if __name__ == '__main__':
    unittest.main(defaultTest='README')

