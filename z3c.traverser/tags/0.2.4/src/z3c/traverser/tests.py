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
"""Pluggable Traverser Tests

$Id$
"""
__docformat__ = "reStructuredText"
import unittest

from zope.testing import doctest
from zope.component import testing


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
        'README.txt',
        setUp=testing.setUp, tearDown=testing.tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
    doctest.DocFileSuite(
        'namespace.txt',
        setUp=testing.setUp, tearDown=testing.tearDown,
        optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))

if __name__ == '__main__':
    unittest.main(default='test_suite')
