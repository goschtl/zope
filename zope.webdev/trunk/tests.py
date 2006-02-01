##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Viewlet tests

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite
from zope.app.testing import setup

from zope.app.testing import ztapi
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.webdev.page import handlePageModification
from zope.webdev.interfaces import IPage
from zope.webdev.page import PageRegistered
from zope.app.component.interfaces.registration import IRegisterable, IRegistered
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.event.objectevent import objectEventNotify
  
def setUp(test):
    setup.placefulSetUp()


def tearDown(test):
    setup.placefulTearDown()

def pageTestSetUp(test):
     setup.placefulSetUp()

     ztapi.subscribe([IObjectModifiedEvent, IPage], None, handlePageModification)
     ztapi.provideAdapter(IPage, IRegistered, PageRegistered)
     ztapi.subscribe([IObjectModifiedEvent], None, objectEventNotify)
    

def test_suite():
    return unittest.TestSuite((
        DocFileSuite('package.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('content.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('page.txt',
                     setUp=pageTestSetUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('container.txt',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('zope.webdev.vocabulary',
                     setUp=setUp, tearDown=tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
