##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Base Components test setup

$Id$
"""
__docformat__ = "reStructuredText"
import doctest
import unittest
from zope.app.testing import placelesssetup, setup

def setUp(test):
    placelesssetup.setUp(test)
    setup.setUpTestAsModule(test, name='README')

def tearDown(test):
    placelesssetup.tearDown(test)

def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
