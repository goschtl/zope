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
$Id$
"""
__docformat__ = 'restructuredtext'

import doctest
import unittest
from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope import component
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.app.keyreference.testing import SimpleKeyReference
from zope.traversing.testing import browserView
from zope.traversing.browser.interfaces import IAbsoluteURL
from z3c.reference.interfaces import IViewReference
from zope.traversing.browser.absoluteurl import AbsoluteURL
from zope.publisher.browser import BrowserPage
from lovely.relation import configurator

from views import ViewReferenceAbsoluteURL

class TestPage(BrowserPage):

    def __call__(self):
        return "testpage"

def setUp(test):
    site = setup.placefulSetUp(True)
    test.globs['site'] = site
    util = configurator.SetUpO2OStringTypeRelationships(site)
    util({})

    component.provideAdapter(SimpleKeyReference)
    component.provideAdapter(ZDCAnnotatableAdapter,
                             provides=IWriteZopeDublinCore)
    intids = IntIds()
    component.provideUtility(intids, IIntIds)
    browserView(IViewReference, '', ViewReferenceAbsoluteURL,
                providing=IAbsoluteURL)
    browserView(None,'index.html',TestPage)

def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    
    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('z3c.reference.browser.widget',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('z3c.reference.browser.views',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

