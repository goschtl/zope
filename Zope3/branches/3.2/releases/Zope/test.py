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

import logging, os, sys, warnings
from distutils.util import get_platform


here = os.path.abspath(os.path.dirname(sys.argv[0]))

# Remove this directory from path:
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != here]

# add build dir to path
PLAT_SPEC = "%s-%s" % (get_platform(), sys.version[0:3])
src = os.path.join(here, "build", "lib." + PLAT_SPEC)
sys.path.insert(0, src) # put at beginning to avoid one in site_packages

from zope.testing import testrunner

defaults = ['--tests-pattern', '^f?tests$', '--test-path', src, '--all', '-u']

# Get rid of twisted.conch.ssh warning
warnings.filterwarnings(
    'ignore', 'PyCrypto', RuntimeWarning, 'twisted[.]conch[.]ssh')

result = testrunner.run(defaults)

# Avoid spurious error during exit. Some thing is trying to log
# something after the files used by the logger have been closed.
logging.disable(999999999)

sys.exit(result)
