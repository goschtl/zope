##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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
"""Container constraint tests

$Id: test_constraints.py 40495 2005-12-02 17:51:22Z efge $
"""
import unittest
from zope.testing import doctest, module

def setUp(test):
    module.setUp(test, 'zope.container.property_txt')

def tearDown(test):
    module.tearDown(test, 'zope.container.property_txt')

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../property.txt',
                             setUp=setUp, tearDown=tearDown),
        ))

if __name__ == '__main__': unittest.main()
