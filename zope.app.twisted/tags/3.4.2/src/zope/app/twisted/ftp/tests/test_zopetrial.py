##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
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
Contains helper functions and monkey patch to integrate twisted trial
tests with the Zope testrunner.

This code will be unneeded when Twisted 2.3 comes out has it contains
code to integrate itself with any pyunit system. But we it need it now to
integrate the test_zope_ftp tests with the zope.testing test runner.

Michael Kerrin <michael.kerrin@openapp.biz>

$Id$
"""
__docformat__="restructuredtext"

import unittest
from zope.testing import doctest
import sys
import os.path
import gc
import re

import zope.testing.testrunner
try:
    orig_configure_logging = zope.testing.testrunner.configure_logging
except AttributeError:
    orig_configure_logging = None

def setUp(test):
    if orig_configure_logging is not None:
        # This setup is for testing the trial integration. This test
        # indirectly calls the zope.testing.testrunner.configure_logging
        # method, which tries to reconfigure the logging. This causes
        # problems with some of the other tests. Nullify this method now;
        # this should OK since the logging should all be set up at this stage.
        zope.testing.testrunner.configure_logging = lambda : None

    test.globs['this_directory'] = os.path.split(__file__)[0]
    test.globs['saved-sys-info'] = (
        sys.path[:],
        sys.argv[:],
        sys.modules.copy(),
        gc.get_threshold(),
        )
    test.globs['testrunner_script'] = __file__


def tearDown(test):
    if orig_configure_logging is not None:
        # redefine the configure_logging method that we nullified in the setUp
        # for these tests.
        zope.testing.testrunner.configure_logging = orig_configure_logging

    sys.path[:], sys.argv[:] = test.globs['saved-sys-info'][:2]
    gc.set_threshold(*test.globs['saved-sys-info'][3])
    sys.modules.clear()
    sys.modules.update(test.globs['saved-sys-info'][2])

def test_suite():
    # copied from zope.testing.testrunner
    import zope.testing.renormalizing
    checker = zope.testing.renormalizing.RENormalizing([
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile('\\\\'), '/'),   # hopefully, we'll make windows happy
        (re.compile('/r'), '\\\\r'), # undo damage from previous
        (re.compile(r'\r'), '\\\\r\n'),
        (re.compile(r'\d+[.]\d\d\d seconds'), 'N.NNN seconds'),
        (re.compile(r'\d+[.]\d\d\d ms'), 'N.NNN ms'),
        (re.compile('( |")[^\n]+testrunner-ex'), r'\1testrunner-ex'),
        (re.compile('( |")[^\n]+testrunner.py'), r'\1testrunner.py'),
        (re.compile(r'> [^\n]*(doc|unit)test[.]py\(\d+\)'),
         r'\1doctest.py(NNN)'),
        (re.compile(r'[.]py\(\d+\)'), r'.py(NNN)'),
        (re.compile(r'[.]py:\d+'), r'.py:NNN'),
        (re.compile(r' line \d+,', re.IGNORECASE), r' Line NNN,'),

        # omit traceback entries for unittest.py or doctest.py from
        # output:
        (re.compile(r'^ +File "[^\n]+(doc|unit)test.py", [^\n]+\n[^\n]+\n',
                    re.MULTILINE),
         r''),
        (re.compile('^> [^\n]+->None$', re.M), '> ...->None'),
        (re.compile('import pdb; pdb'), 'Pdb()'), # Py 2.3
        ])
    
    suites = [
        doctest.DocFileSuite('trial.txt',
                             setUp = setUp, tearDown = tearDown,
                             optionflags = doctest.ELLIPSIS,
                             checker = checker),
        ]

    return unittest.TestSuite(suites)
