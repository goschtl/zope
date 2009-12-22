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
""" z3ext.security tests

$Id$
"""
__docformat__ = "reStructuredText"

import unittest, doctest
from zope import interface, schema, component
from zope.component.testing import tearDown
from zope.security.management import endInteraction
from zope.securitypolicy.tests import test_zopepolicy
from z3ext.security.grantinfo import ExtendedGrantInfo
from z3ext.security.interfaces import IExtendedGrantInfo


def setUp(test):
    test_zopepolicy.setUp(test)
    component.provideAdapter(
        ExtendedGrantInfo, (interface.Interface,), IExtendedGrantInfo)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'grantinfo.txt', setUp=setUp, tearDown=tearDown),
            doctest.DocFileSuite(
                'securitypolicy.txt',setUp=setUp, tearDown=tearDown),
            doctest.DocFileSuite(
                'zcml.txt', setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            doctest.DocTestSuite(
                'z3ext.security.vocabulary', setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
            ))
