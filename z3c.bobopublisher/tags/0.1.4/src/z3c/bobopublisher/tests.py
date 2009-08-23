##############################################################################
#
# Copyright (c) 2009 Fabio Tranchitella <fabio@tranchitella.it>
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

import unittest

from z3c.bobopublisher.browser import BrowserPage

from zope.testing import doctest, doctestunit


docfiles = [
    'README.txt',
]

doctests = [
    'z3c.bobopublisher.absoluteurl',
    'z3c.bobopublisher.browser',
    'z3c.bobopublisher.middleware.security',
]


def test_suite():
    tests = []
    for d in doctests:
        tests.append(doctestunit.DocTestSuite(d, optionflags=doctest.ELLIPSIS))
    for d in docfiles:
        tests.append(doctest.DocFileSuite(d, optionflags=doctest.ELLIPSIS))
    return unittest.TestSuite(tests)


class TestBrowserPage(BrowserPage):
    """Test browser page"""

    def __call__(self):
        return u'TEST PAGE'


class TestAttributeBrowserPage(BrowserPage):
    """Test browser page"""

    def attribute(self):
        return u'ATTRIBUTE'
