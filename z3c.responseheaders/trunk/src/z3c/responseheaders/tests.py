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

from zope.app.publication.interfaces import IBeforeTraverseEvent
from zope.publisher.interfaces.browser import IBrowserView
import doctest
import setter
import zope.app.testing.setup
import zope.component


def setUp(test):
    zope.app.testing.setup.placefulSetUp()
    zope.component.provideHandler(setter.onBrowserViewBeforeTraverse,
                                  (IBrowserView, IBeforeTraverseEvent))

def tearDown(test):
    zope.app.testing.setup.placefulTearDown()


def test_suite():
    return doctest.DocFileSuite(
        'README.txt',
        setUp=setUp, tearDown=tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
        )
