##############################################################################
#
# Copyright (c) 2007 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Resource License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: __init__.py 40 2007-02-21 09:18:28Z roger.ineichen $
"""
__docformat__ = 'restructuredtext'

import doctest
import unittest
from zope.app.testing import setup
from zope.testing.doctestunit import DocFileSuite

from z3c.website import testing


def setUp(test):
    test.globs = {'root': setup.placefulSetUp(True)}


def tearDown(test):
    setup.placefulTearDown()


def test_suite():

    return unittest.TestSuite((
        testing.FunctionalDocFileSuite('README.txt'),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

