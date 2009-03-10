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
"""Tests z3c.ownership package

$Id$
"""
import unittest
from zope.testing import doctest, cleanup
from zope.component import eventtesting

from zope.annotation.interfaces import IAnnotatable
from zope.annotation.attribute import AttributeAnnotations
from zope.app.security.interfaces import IAuthentication
from zope.app.security.principalregistry import principalRegistry
from zope.component import provideAdapter, provideUtility, provideHandler
from zope.securitypolicy.principalrole import AnnotationPrincipalRoleManager

from z3c.ownership.ownership import Ownership
from z3c.ownership.subscriber import setOwner

def setUp(test):
    cleanup.setUp()
    eventtesting.setUp()
    provideAdapter(AttributeAnnotations)
    provideAdapter(AnnotationPrincipalRoleManager, adapts=(IAnnotatable, ))
    provideAdapter(Ownership)
    provideHandler(setOwner)
    provideUtility(principalRegistry, IAuthentication)
    test.globs = {'authentication': principalRegistry}

def tearDown(test):
    cleanup.tearDown()

def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            'README.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
        )
