##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors
#
##############################################################################
"""
$Id$
"""
import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import placelesssetup, setup


def setUp(test):
    placelesssetup.setUp(test)
    setup.setUpTestAsModule(test, 'README')

def tearDown(test):
    setup.tearDownTestAsModule(test)
    placelesssetup.tearDown(test)

def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'README.txt',
            setUp=setUp, tearDown=tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))
