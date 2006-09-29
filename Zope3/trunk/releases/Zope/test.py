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
"""Test script for running unit tests in a distribution root.

The functional tests can't be run since we don't have enough of the
package configuration in a usable state.  The functional tests can be
run from an installation.

$Id$
"""
import sys, os, warnings, logging
from distutils.util import get_platform

# Insert build path
PLAT_SPEC = "%s-%s" % (get_platform(), sys.version[0:3])
here = os.path.dirname(os.path.realpath(__file__))
lib = os.path.join(here, "build", "lib." + PLAT_SPEC)
sys.path.insert(0, lib)
# Remove this directory from path:
here = os.path.abspath(os.path.dirname(sys.argv[0]))
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != here]

from zope.testing import testrunner

# Get rid of twisted.conch.ssh warning
warnings.filterwarnings(
    'ignore', 'PyCrypto', RuntimeWarning, 'twisted[.]conch[.]ssh')

defaultargs = ['--tests-pattern', '^f?tests$', '--test-path', lib,
               '--unit', '--verbose']
result = testrunner.run(defaultargs)

# Note, the logging system has bugs, fixed in Python 2.5 that cause spurious
# errors on exit.  We'll execute a fairly voilent suicide to try to avoid
# these.  Given that this is just a test runner, this should be OK.

# Avoid spurious error during exit. Some thing is trying to log
# something after the files used by the logger have been closed.
logging.disable(999999999)

# Because we're about to use os._exit, we flush output so we don't miss any.
sys.stdout.flush()
sys.stderr.flush()
os._exit(result)

# TODO according to the comment above:
#      with python 2.5 the above 3 lines should be again:
# sys.exit(result)
