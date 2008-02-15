# -*- coding: utf-8 -*-
###############################################################################
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
###############################################################################
"""Tests for the Book Documentation Module

$Id$
"""
__docformat__ = "reStructuredText"
import unittest
import zope.component

from zope.testing import doctest, doctestunit
from zope.app import principalannotation
from zope.copypastemove import PrincipalClipboard
from zope.app.testing import placelesssetup, setup, ztapi


def setUp(test):
    placelesssetup.setUp(test)
    setup.setUpTraversal()

    zope.component.provideUtility(
        principalannotation.PrincipalAnnotationUtility(),
        principalannotation.IPrincipalAnnotationUtility)
    zope.component.provideAdapter(
        principalannotation.annotations,
        adapts=(None,))
    zope.component.provideAdapter(
        PrincipalClipboard)

def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
            setUp=setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))


if __name__ == '__main__':
    unittest.main(default='test_suite')
