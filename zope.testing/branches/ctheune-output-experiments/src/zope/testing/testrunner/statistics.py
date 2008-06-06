##############################################################################
#
# Copyright (c) 2004-2008 Zope Corporation and Contributors.
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
"""Test runner statistics

$Id: __init__.py 86218 2008-05-03 14:17:26Z ctheune $
"""

import os
import time
import zope.testing.testrunner.feature


class Statistics(zope.testing.testrunner.feature.Feature):

    active = True
    layers_run = 0
    tests_run = 0

    def global_setup(self):
        print 'User: %s' % os.getlogin()
        print 'Platform: %s' % ' '.join(os.uname())

    def late_setup(self):
        self.start_time = time.time()

    def early_teardown(self):
        self.end_time = time.time()

    def global_teardown(self):
        self.total_time = self.end_time - self.start_time

    def layer_setup(self, layer):
        self.previous_tests = self.runner.ran
        self.previous_errors = len(self.runner.errors)
        self.previous_failures = len(self.runner.failures)
        self.layers_run += 1
        print 'Running tests in layer: %s' % layer.__name__

    def layer_teardown(self, layer):
        print 'Finished tests in layer: %s' % layer.__name__
