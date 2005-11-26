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

$Id: tests.py 39461 2005-10-15 10:45:13Z srichter $
"""
__docformat__ = 'restructuredtext'

import unittest
import zope.component.interfaces
import zope.interface
from zope.testing import doctest, doctestunit

from zope.app.container import contained
from zope.app.renderer import rest
from zope.app.testing import placelesssetup, setup, ztapi


def setUp(test):
    setup.placefulSetUp(True)
    zope.component.provideAdapter(contained.NameChooser,
                                  (zope.interface.Interface,))
    # Register Renderer Components
    ztapi.provideUtility(zope.component.interfaces.IFactory,
                         rest.ReStructuredTextSourceFactory,
                         'zope.source.rest')
    ztapi.browserView(rest.IReStructuredTextSource, '',
                      rest.ReStructuredTextToHTMLRenderer)

def tearDown(test):
    setup.placefulTearDown()

def test_suite():
    return unittest.TestSuite((
        doctestunit.DocFileSuite('README.txt',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        doctestunit.DocFileSuite('session.txt',
                     setUp=setUp, tearDown=tearDown,
                     globs={'pprint': doctestunit.pprint},
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        doctestunit.DocFileSuite('testbrowser.txt',
                     setUp=setUp, tearDown=tearDown,
                     globs={'pprint': doctestunit.pprint},
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        doctestunit.DocFileSuite('directives.txt',
                     setUp=placelesssetup.setUp,
                     tearDown=placelesssetup.tearDown,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
