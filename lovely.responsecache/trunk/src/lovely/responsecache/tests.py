##############################################################################
#
# Copyright (c) 2006-2007 Lovely Systems and Contributors.
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

from zope import interface
from zope import component

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import functional
from zope.app.testing import setup
from z3c.configurator import configurator
from z3c.testing import layer
from lovely.memcached.interfaces import IMemcachedClient

from view import ResponseCacheSettings

class IMyView(interface.Interface):
    pass

class MyCacheSettings(ResponseCacheSettings):
    pass


def appSetUp(app):
    configurator.configure(app, {},
                           names = ['lovely.memcachedclient'])
    cache = component.getUtility(IMemcachedClient,
                                 context=app)
    cache.invalidateAll()

layer.defineLayer('ResponseCacheLayer', zcml='ftesting.zcml',
                  appSetUp=appSetUp,
                  clean=True)

def setUp(test):
    root = setup.placefulSetUp(True)
    test.globs['root'] = root
    test.globs['IMyView'] = IMyView

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    level1Suites = (
        DocFileSuite(
            'zcml.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        DocFileSuite(
            'credentials.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        )
    fsuite = functional.FunctionalDocFileSuite('BROWSER.txt')
    fsuite.layer=ResponseCacheLayer
    level2Suites = (
        DocFileSuite(
        'README.txt', setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        ),
        fsuite,
        )
    for suite in level2Suites:
        suite.level = 2
    return unittest.TestSuite(level1Suites + level2Suites)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
