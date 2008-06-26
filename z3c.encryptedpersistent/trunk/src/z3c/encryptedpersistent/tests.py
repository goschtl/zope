##############################################################################
#
# Copyright (c) 2008 by JSA Technologies, Inc
#
##############################################################################
"""
$Id$
"""
import unittest
import doctest
from zope.testing.doctestunit import DocFileSuite
from zope.app.testing import placelesssetup, setup


def test_suite():
    return unittest.TestSuite((
        DocFileSuite(
            'README.txt',
            setUp=placelesssetup.setUp, tearDown=placelesssetup.tearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS),
        ))