#!/usr/bin/env python
##############################################################################
#
# Copyright (c) 2008 Vanguardistas and Contributors.
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
