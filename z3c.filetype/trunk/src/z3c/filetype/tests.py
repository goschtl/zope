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
""" tests setup

$Id$
"""
import doctest, unittest
from zope.app.testing import setup
from zope import component

from z3c.filetype import size, typeablefile
    

def setUp(test):
    setup.placelessSetUp()

    component.provideAdapter(size.JPGFileSized)
    component.provideAdapter(size.GIFFileSized)
    component.provideAdapter(size.PNGFileSized)

    component.provideAdapter(typeablefile.TypeableFileData)
    component.provideHandler(typeablefile.handleCreated)
    component.provideHandler(typeablefile.handleModified)


def test_suite():
    return unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp, tearDown=setup.placelessTearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            doctest.DocFileSuite(
                'converter.txt',
                setUp=setUp, tearDown=setup.placelessTearDown,
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            doctest.DocFileSuite(
                'magic.txt',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            doctest.DocTestSuite(
                'z3c.filetype.api',
                optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                ),
            ))
