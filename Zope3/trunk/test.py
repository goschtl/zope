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
import logging, os, sys, warnings

here = os.path.abspath(os.path.dirname(sys.argv[0]))

# Remove this directory from path:
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != here]

# add src to path
src = os.path.join(here, 'src')
sys.path.insert(0, src) # put at beginning to avoid one in site_packages

from zope.testing import testrunner

defaults = ['--tests-pattern', '^f?tests$', '--test-path', src]
defaults += ['-m',
             '!^('
             'ZConfig'
             '|'
             'BTrees'
             '|'
             'persistent'
             '|'
             'ThreadedAsync'
             '|'
             'transaction'
             '|'
             'ZEO'
             '|'
             'ZODB'
             '|'
             'twisted'
             '|'
             'zdaemon'
             '|'
             'zope[.]testing'
             '|'
             ')[.]']

# Get rid of twisted.conch.ssh warning
warnings.filterwarnings(
    'ignore', 'PyCrypto', RuntimeWarning, 'twisted[.]conch[.]ssh')

result = testrunner.run(defaults)

# Avoid spurious error during exit. Some thing is trying to log
# something after the files used by the logger have been closed.
logging.disable(999999999)
