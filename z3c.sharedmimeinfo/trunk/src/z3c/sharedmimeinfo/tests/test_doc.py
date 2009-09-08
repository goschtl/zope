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
"""Tests for z3c.sharedmimeinfo functionality.

$Id$
"""
import os
import unittest

from zope.testing import doctest
from zope.component import provideUtility

from z3c.sharedmimeinfo.mimetype import mimeTypesTranslationDomain

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'sample_data')

def openSample(extension):
    return open(os.path.join(SAMPLE_DATA_DIR, 'sample.' + extension))

def setUp(test):
    provideUtility(mimeTypesTranslationDomain, name='shared-mime-info')
    test.globs['openSample'] = openSample

def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            '../README.txt',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    )
