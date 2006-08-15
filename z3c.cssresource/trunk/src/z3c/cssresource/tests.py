##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tag test setup

$Id$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest
import zope.component
from zope.app.testing import placelesssetup
from zope.testing.doctestunit import DocFileSuite
from zope.traversing import testing
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import view


def setUp(test):
    placelesssetup.setUp(test)
    testing.setUp()
    zope.component.provideAdapter(view, (None, None), ITraversable, name="view")


def test_suite():

    return unittest.TestSuite((
        DocFileSuite('README.txt',
                     setUp=setUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('zcml.txt',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
