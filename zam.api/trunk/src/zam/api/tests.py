##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
$Id: tests.py 69742 2006-08-23 22:17:00Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import doctest
import unittest
from zope.testing import doctestunit
from zope.app.testing import setup


def setUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site
    setup.setUpTestAsModule(test, name='README')

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('README.txt', 
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
