##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""Support for test checkers

Test checkers are used to identify tests that do not clean up after themselves.
"""

import sys


class AbstractTestChecker(object):
    """A useful base class for test checkers.

    You are not required to subclass it (this is Python after all!), but you
    may find it convenient.

    Subclasses of AbstractTestChecker take a snapshot of some global state
    before each test is run, then take another snapshot after the test is
    finished, and compare those snapshots.  If there are differences,
    a warning is printed to stderr.
    """

    what = 'something' # change this in subclasses

    def startTest(self, test):
        self.old_state = self.takeSnapshot()

    def stopTest(self, test):
        new_state = self.takeSnapshot()
        if self.old_state != new_state:
            self.warn("%s changed %s" % (test, self.what))
            self.showDifferences(self.old_state, new_state)
        del self.old_state

    def startLayer(self, layer):
        self.old_layer_state = self.takeSnapshot()

    def stopLayer(self, layer):
        new_layer_state = self.takeSnapshot()
        if self.old_layer_state != new_layer_state:
            self.warn("%s changed %s" % (layer, self.what))
            self.showDifferences(self.old_layer_state, new_layer_state)
        del self.old_layerstate

    def takeSnapshot(self):
        """Take a snapshot of the global state.

        Returns something that can be compared.
        """
        raise NotImplementedError('override in subclasses')

    def showDifferences(self, old_state, new_state):
        """Show the differences between old and new state.

        Does nothing by default, but can be overridden.
        """
        pass

    def warn(self, msg):
        """Print a message to stderr."""
        # It is a good idea to print a newline at the beginning, because the
        # test runner may be doing fancy formatting and we do not want the
        # message to appear somewhere in the middle of another line.
        print >> sys.stderr, "\n" + msg

