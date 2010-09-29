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

import os
import doctest
import unittest
import zope
from zope.traversing.interfaces import ITraverser, ITraversable

from doctest import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from zope.app.intid import IntIds
from zope.app.intid.interfaces import IIntIds
from zope import component
from zope.dublincore.annotatableadapter import ZDCAnnotatableAdapter
from zope.dublincore.interfaces import IWriteZopeDublinCore
from zope.dublincore.testing import setUpDublinCore
from zope.traversing.testing import browserView
from zope.publisher.browser import BrowserPage
from zope.traversing.namespace import resource, view
from zope.traversing.testing import setUp as setUpTraversing

from zope.app.keyreference.testing import SimpleKeyReference
from zope.app.testing.ztapi import browserResource

from lovely.relation import configurator


class TestPage(BrowserPage):

    def __call__(self):
        return "testpage"

class Resource(object):

    def __init__(self, request):
        pass

def setUp(test):

    site = setup.placefulSetUp(True)
    test.globs['site'] = site
    util = configurator.SetUpO2OStringTypeRelationships(site)
    util({})

    setUpTraversing()
    zope.component.provideAdapter(resource, (None,), ITraversable, name="resource")
    zope.component.provideAdapter(resource, (None, None), ITraversable, name="resource")
    zope.component.provideAdapter(view, (None,), ITraversable, name="view")
    zope.component.provideAdapter(view, (None, None), ITraversable, name="view")
    browserResource('imagetool.swf', Resource)

    component.provideAdapter(SimpleKeyReference)
    component.provideAdapter(ZDCAnnotatableAdapter,
                             provides=IWriteZopeDublinCore)
    intids = IntIds()
    component.provideUtility(intids, IIntIds)
    browserView(None,'index.html',TestPage)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():

    return unittest.TestSuite((
        DocFileSuite('serialize.txt',
                     setUp=setUp,tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
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

