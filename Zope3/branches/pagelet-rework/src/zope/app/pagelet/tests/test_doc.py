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
"""Pagelet tests

$Id$
"""
__docformat__ = 'restructuredtext'

import unittest
import zope.interface
from zope.testing import doctest
from zope.testing.doctestunit import DocTestSuite, DocFileSuite
from zope.app.testing import setup

from zope.app.pagelet import interfaces


class TestPagelet(object):

    def doSomething(self):
        return u'something'


class TestPagelet2(object):

    def __call__(self):
        return u'called'


class ITestSlot(zope.interface.Interface):
    '''A slot for testing purposes.'''
zope.interface.directlyProvides(ITestSlot, interfaces.IPageletSlot)


def test_suite():
    return unittest.TestSuite((
        DocTestSuite('zope.app.pagelet.tales'),
        DocFileSuite('../README.txt',
                     setUp=setup.placefulSetUp,
                     tearDown=setup.placefulTearDown(),
                     ),
        DocFileSuite('../directives.txt',
                     setUp=setup.placefulSetUp,
                     tearDown=setup.placefulTearDown(),
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
