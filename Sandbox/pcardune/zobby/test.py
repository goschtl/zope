#!/usr/bin/env python2.4
##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id: test.py 72 2007-03-26 15:31:12Z rineichen $
"""

import logging, os, sys, warnings

if sys.version_info < (2, 4):
    print >> sys.stderr, '%s: need Python 2.4 or later.' % sys.argv[0]
    print >> sys.stderr, 'Your python is %s' % sys.version
    sys.exit(1)

here = os.path.abspath(os.path.dirname(sys.argv[0]))


# Remove this directory from path:
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != here]


# Remove Zope3 directory from path:
zope3Root = os.path.join(here, 'Zope3')
sys.path[:] = [p for p in sys.path if os.path.abspath(p) != zope3Root]


# Replace the directory of this wrapper script with src and Zope3/src
# source directories
sys.path[:1] = [os.path.join(here, 'src'), os.path.join(here, 'Zope3', 'src')]


# add Zope3/src and src to path, put at beginning to avoid one in site_packages
zope3src = os.path.join(here, 'Zope3', 'src')
src = os.path.join(here, 'src')
sys.path.insert(0, zope3src)
sys.path.insert(0, src)


from zope.testing import testrunner

# the duplicated *--test-path* variable seems to work. ri
defaults = ['--tests-pattern', '^f?tests$', '--test-path', src, '--test-path', zope3src]
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

sys.exit(result)
