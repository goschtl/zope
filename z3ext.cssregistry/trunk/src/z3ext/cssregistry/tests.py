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
""" z3ext.cssregistry tests"""

from zope import interface, schema
from zope.component import provideAdapter, testing
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import view
from zope.traversing.testing import setUp as traversingSetUp
import unittest, doctest
import zope.browserresource.file


def setUp(test):
    testing.setUp()
    traversingSetUp()
    provideAdapter(view, (None, None), ITraversable, name="view")
    provideAdapter(zope.browserresource.file.FileETag)


def tearDown(test):
    testing.tearDown()


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
