##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""XXX short summary goes here.

$Id: dut.py,v 1.1 2003/12/17 13:30:17 jim Exp $
"""
import unittest
from doctest import DocTestSuite

def test_xxx():
    """
    """

def test_suite():
    return unittest.TestSuite((

        # Uncomment the following line if there are tests in this module:
        # DocTestSuite(),

        # Uncomment the following line if there are tests in the regular
        # sources.  Pass the dotted name of the module:
        # DocTestSuite('mypackage.mymodule'),
        
        ))

if __name__ == '__main__': unittest.main()
