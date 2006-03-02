#! /usr/bin/env python
##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Script to run all the regression tests for zpkgtools."""

import os
import sys
import unittest

if __name__ == "__main__":
    __file__ = sys.argv[0]

TESTDIR = os.path.dirname(os.path.abspath(__file__))

PKGDIR = os.path.dirname(TESTDIR) # the package directory
TOPDIR = os.path.dirname(PKGDIR)


def test_suite():
    from zpkgsetup.tests.runtests import make_directory_suite
    return make_directory_suite("zpkgtools.tests", TESTDIR)


if __name__ == "__main__":
    if TOPDIR not in sys.path:
        sys.path.insert(0, TOPDIR)
    from zpkgsetup.tests.runtests import MyTestProgram
    MyTestProgram(defaultTest="test_suite")
