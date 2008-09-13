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

import unittest
import itertools

from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import setup
from zope.configuration import xmlconfig

import z3c.pt.compat

def setUp(test):
    root = setup.placefulSetUp(site=True)
    test.globs['root'] = root

def tearDown(test):
    setup.placefulTearDown()

def setUpZPT(suite):
    z3c.pt.compat.config.disable()
    setUp(suite)
    
def setUpZ3CPT(suite):
    z3c.pt.compat.config.enable()
    setUp(suite)
    xmlconfig.XMLConfig('configure.zcml', z3c.pt)()

def test_suite():
    tests = ((
        DocFileSuite('README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,
            ),
        DocFileSuite('zcml.txt', setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS,)
        ) for setUp in (setUpZPT, setUpZ3CPT,))

    return unittest.TestSuite(itertools.chain(*tests))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
