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
"""Test script

$Id$
"""
import sys, os

here = os.path.abspath(os.path.dirname(sys.argv[0]))

# Remove this directory from path:
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != here]

# add src to path
src = os.path.join(here, 'src')
sys.path.insert(0, src) # put at beginning to avoid one in site_packages

from zope.testing import testrunner

defaults = ['--tests-pattern', '^f?tests$', '--test-path', src]

sys.exit(testrunner.run(defaults))
