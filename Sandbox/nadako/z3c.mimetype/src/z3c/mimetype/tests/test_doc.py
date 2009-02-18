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
import os
import unittest

from zope.testing import doctest
from zope.component import provideUtility

from z3c.mimetype.utility import globalMIMETypesUtility
from z3c.mimetype.mimetype import mimeTypesTranslationDomain

def setUp(test):
    provideUtility(globalMIMETypesUtility)
    provideUtility(mimeTypesTranslationDomain, name='shared-mime-info')
    test.globs['SAMPLE_DATA_DIR'] = os.path.join(os.path.dirname(__file__), 'sample_data')

def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite(
            '../README.txt',
            setUp=setUp,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS)
    )
