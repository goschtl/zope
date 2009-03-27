##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Test Setup.

$Id$
"""
import unittest
import zope.testing.doctest
from z3c.builder.core import testing

def test_suite():
    return unittest.TestSuite((

        zope.testing.doctest.DocFileSuite(
            'README.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        zope.testing.doctest.DocFileSuite(
            'content.txt',
            setUp=testing.buildSetUp, tearDown=testing.buildTearDown,
            optionflags=zope.testing.doctest.NORMALIZE_WHITESPACE |
                        zope.testing.doctest.ELLIPSIS),

        ))
