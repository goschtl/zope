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
"""Menu tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest

from zope import component

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

from zope.app.intid.interfaces import IIntIds
from zope.app.intid import IntIds
from zope.app import intid
from zope.app.keyreference import testing

from zope.app.testing import setup


def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root
    sm = root.getSiteManager()
    sm['intids'] = IntIds()
    component.provideUtility(sm['intids'], IIntIds)
    setup.setUpAnnotations()
    component.provideAdapter(testing.SimpleKeyReference)
    component.provideHandler(intid.addIntIdSubscriber)
    component.provideHandler(intid.removeIntIdSubscriber)


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
        DocFileSuite('README.txt',
             setUp=setUp, tearDown=tearDown,
             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
        DocFileSuite('property.txt',
             setUp=setUp, tearDown=tearDown,
             optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
             ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

