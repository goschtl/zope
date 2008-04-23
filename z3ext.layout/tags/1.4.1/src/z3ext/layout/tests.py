##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED 'AS IS' AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" 

$Id$
"""
import unittest, doctest
from zope import interface
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
from zope.app.container.sample import SampleContainer

class IFolder1(interface.Interface):
    pass

class IFolder1_1(interface.Interface):
    pass

class IFolder1_1_1(interface.Interface):
    pass


class Folder(SampleContainer):
    pass


class MyLayout(object):

    title = u'My layout'


def setUp(test):
    root = setup.placefulSetUp(site=True)
    root.__name__ = 'root'
    test.globs['root'] = root


def tearDown(test):
    setup.placefulTearDown()


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=tearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            doctest.DocFileSuite(
                'pagelet.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))
