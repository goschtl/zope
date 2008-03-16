###############################################################################
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
###############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import unittest
from zope.testing import doctest
from zope.app.testing import setup
from zope.app.testing import placelesssetup


def siteSetUp(test):
    site = setup.placefulSetUp(site=True)
    test.globs['rootFolder'] = site


def siteTearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=siteSetUp, tearDown=siteTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocFileSuite('group.txt',
            setUp=siteSetUp, tearDown=siteTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        doctest.DocTestSuite('z3c.authentication.simple.principal',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown),
        doctest.DocTestSuite('z3c.authentication.simple.group',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown),
        doctest.DocFileSuite('vocabulary.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
