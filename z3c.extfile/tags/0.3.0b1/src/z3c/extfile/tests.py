##############################################################################
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
##############################################################################
"""
$Id$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest

from zope.testing.doctestunit import DocFileSuite, DocTestSuite
from zope.app.testing import setup
from paste.fixture import setup_module
from paste.fixture import TestApp
import os
from zope.app.appsetup import product

here = os.path.dirname(__file__)

def setUpWSGI(test):
    test.globs['app'] = TestApp('config:testdata/paste.ini',
                                relative_to=here)

def setUpNoEnv(test):
    if os.environ.has_key('EXTFILE_STORAGEDIR'):
        del os.environ['EXTFILE_STORAGEDIR']
    product._configs.clear()

def test_suite():

    return unittest.TestSuite(
        (
        DocFileSuite('hashdir.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('namespace.txt',
                     setUp=setup.placefulSetUp,
                     tearDown=lambda x: setup.placefulTearDown(),
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('processor.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('filter.txt', setUp=setUpWSGI,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('property.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('adapter.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('browser/widget.txt',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocTestSuite('z3c.extfile.utility',
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('testing.txt', setUp=setUpNoEnv,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        DocFileSuite('zcml.txt', setUp=setUpNoEnv,
                     optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
                     ),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

