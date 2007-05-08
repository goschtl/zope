##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
$Id: __init__.py 70825 2006-10-20 01:34:05Z rogerineichen $
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
from zope.app.testing import placelesssetup


def setUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
