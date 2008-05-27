##############################################################################
#
# Copyright (c) 2006-2008 Lovely Systems GmbH. All Rights Reserved.
#
# This software is subject to the provisions of the Lovely Visible Source
# License, Version 1.0 (LVSL).  A copy of the LVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""
$Id$
"""
__docformat__ = 'restructuredtext'

import doctest, unittest

from zope import component
from zope.component import eventtesting
from zope.app.testing import setup
from zope.testing.doctest import DocFileSuite, DocTestSuite

from z3c.configurator.configurator import SchemaConfigurationPluginBase
from zope.app.component.testing import PlacefulSetup
from factory import reset
from zope.testing.cleanup import addCleanUp

class ConfOne(SchemaConfigurationPluginBase):

    def __call__(self, data):
        print "called: %r, on %r with data: %r" % (
            self.__class__.__name__, self.context.__name__, data)

class ConfTwo(ConfOne):
    pass

def setUp(test):
    addCleanUp(reset)
    component.provideHandler(eventtesting.events.append, (None,))

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    uSuites = (
        DocFileSuite('README.txt', setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('lovely.zetup.factory',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('lovely.zetup.config',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('lovely.zetup.browser.views',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('publication.txt', setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        )
    return unittest.TestSuite(uSuites)
