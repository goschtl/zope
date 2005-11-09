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

from zope.testing import doctest


def sys_path_setUp(self):
    self.__old_path = sys.path[:]

def sys_path_tearDown(self):
    sys.path[:] = self.__old_path


def test_suite():
    return doctest.DocFileSuite(
        "README.txt", setUp=sys_path_setUp, tearDown=sys_path_tearDown)
