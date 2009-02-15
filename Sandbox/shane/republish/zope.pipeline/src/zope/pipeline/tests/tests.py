##############################################################################
#
# Copyright (c) 2009 Zope Corporation and Contributors.
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
"""Tests of this package"""

import unittest

from zope.testing import doctest
from zope.testing.cleanup import cleanUp
from zope.configuration.xmlconfig import XMLConfig

import zope.pipeline

def setUp(doctest):
    cleanUp()
    XMLConfig('meta.zcml', zope.pipeline)()
    XMLConfig('configure.zcml', zope.pipeline)()

def tearDown(doctest):
    cleanUp()

def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite('autotemp_test.txt'),
        doctest.DocFileSuite('basicconfig.txt', setUp=setUp, tearDown=tearDown),
    ])

if __name__ == '__main__':
    unittest.main()
