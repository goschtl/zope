#!/usr/bin/env python
"""
Run all unit tests.
"""

import unittest
import sys

def main():
    sys.path.insert(0, 'src')
    suite = unittest.TestSuite()
    from vanguardistas.pydebdep.tests.test_doctest import test_suite
    suite.addTest(test_suite())
    runner = unittest.TextTestRunner(verbosity=1)
    runner.run(suite)

if __name__ == '__main__':
    main()
