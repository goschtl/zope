##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
from zope import interface, schema
from zope.app.testing import setup, ztapi
from zope.security.management import endInteraction
from zope.securitypolicy.tests import test_zopepolicy
from z3ext.security.grantinfo import ExtendedGrantInfo
from z3ext.security.interfaces import IExtendedGrantInfo


def setUp(test):
    test_zopepolicy.setUp(test)
    ztapi.provideAdapter(interface.Interface, IExtendedGrantInfo, ExtendedGrantInfo)

def tearDown(test):
    setup.placelessTearDown()


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'grantinfo.txt',setUp=setUp, tearDown=tearDown),
            doctest.DocFileSuite(
                'securitypolicy.txt',setUp=setUp, tearDown=tearDown),
            ))
