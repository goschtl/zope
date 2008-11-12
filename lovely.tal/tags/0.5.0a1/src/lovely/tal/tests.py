##############################################################################
#
# Copyright (c) 2007 Lovely Systems and Contributors.
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
$Id$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite

def setUp(test):
    setup.placefulSetUp()

def tearDown(test):
    setup.placefulTearDown()

def test_suite():

   suite = unittest.TestSuite(
        (
        DocFileSuite('README.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

   return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
