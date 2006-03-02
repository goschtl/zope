#!/usr/bin/env python2.4
##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Convenience test script for Jim.

$Id$
"""
import os.path
import sys

try:
    from zope.testing import testrunner
except ImportError:
    if sys.argv[1:]:
        # We got args, but we're not about to support them here.
        print >>sys.stderr, \
              "arguments only supported when zope.testing is available"
        sys.exit(2)

    def test_suite():
        from zpkgsetup.tests import runtests
        suite = runtests.test_suite()
        from zpkgtools.tests import runtests
        suite.addTest(runtests.test_suite())
        return suite

    from zpkgsetup.tests import runtests
    runtests.MyTestProgram(defaultTest="test_suite")
else:
    # 1. search for tests in starting in this directory
    # 2. there are only unit tests, not functional tests
    here = os.path.dirname(os.path.realpath(__file__))
    defaults = ['--tests-pattern', '^tests$', "--test-path", here, '-v']
    result = testrunner.run(defaults)
