##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Test resource machinery.

"""
__docformat__ = "reStructuredText"

import sys
import unittest

import zope.resource.reference

from zope.testing import doctest

try:
    import pkg_resources
except ImportError:
    pkg_resources = None


def sys_path_setUp(self):
    self.__old_path = sys.path[:]

def sys_path_tearDown(self):
    sys.path[:] = self.__old_path


# If the pkg_resources module is available, this setUp/tearDown pair
# can be used to hack zope.resource to think it isn't.  This is done
# to ensure test coverage even when the module is present.

def pkg_resources_setUp(self):
    sys_path_setUp(self)
    self.__old_pkg_resources = pkg_resources
    zope.resource.reference.pkg_resources = None

def pkg_resources_tearDown(self):
    sys_path_tearDown(self)
    zope.resource.pkg_resources = self.__old_pkg_resources


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite(
        "README.txt",
        setUp=sys_path_setUp, tearDown=sys_path_tearDown))
    if pkg_resources is not None:
        suite.addTest(doctest.DocFileSuite(
            "README.txt",
            setUp=pkg_resources_setUp, tearDown=pkg_resources_tearDown))
    return suite
