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

import unittest

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite

from zope.app.testing.setup import (placefulSetUp,
                                    placefulTearDown)


def setUp(test):
    root = placefulSetUp(site=True)
    test.globs['root'] = root

def tearDown(test):
    placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
             setUp=setUp, tearDown=tearDown,
             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
        DocFileSuite('remotemail.txt',
             setUp=setUp, tearDown=tearDown,
             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
        DocTestSuite('lovely.mail.testing',
             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

