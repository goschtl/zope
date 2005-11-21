##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Simple Text Controller implementation.

$Id$
"""
__docformat__ = "reStructuredText"
from zope.testing import doctest


class PermissiveOutputChecker(object):

    def check_output(self, want, got, optionflags):
        return True


class ExampleRunner(doctest.DocTestRunner):
    """Example Runner"""

    def __init__(self, globs, checker=None, verbose=None, optionflags=0):
        if checker is None:
            checker = PermissiveOutputChecker()
        doctest.DocTestRunner.__init__(self, checker, verbose, optionflags)
        self.globs = globs

    def run(self, example, compileflags=None, out=None):
        """ """
        test = doctest.DocTest([example], self.globs, '', '', 0, '')
        return doctest.DocTestRunner.run(self, test, clear_globs=False)
