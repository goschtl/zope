##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
__docformat__ = "reStructuredText"

import unittest

from zope.testing import doctest
from zope.testing import doctestunit

from z3c.authentication.cookie import testing


def test_suite():
    return unittest.TestSuite((
        testing.FunctionalDocFileSuite('BROWSER.txt'),
        doctest.DocTestSuite('z3c.authentication.cookie.session',
            setUp=testing.siteSetUp, tearDown=testing.siteTearDown),
        doctest.DocTestSuite('z3c.authentication.cookie.plugin',
            setUp=testing.siteSetUp, tearDown=testing.siteTearDown),
        doctestunit.DocFileSuite('README.txt',
            setUp=testing.siteSetUp, tearDown=testing.siteTearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
