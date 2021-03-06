##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Registration tests

$Id: test_registration.py 40495 2005-12-02 17:51:22Z efge $
"""
import unittest
from zope.testing import doctest, module

def setUp(test):
    module.setUp(test, 'zope.app.fssync.registration_txt')

def tearDown(test):
    module.tearDown(test, 'zope.app.fssync.registration_txt')

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('../registration.txt',
                             setUp=setUp, tearDown=tearDown,
                             optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS),
        ))

if __name__ == '__main__': unittest.main()
