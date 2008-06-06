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
"""Filter which tests to run.

$Id: __init__.py 86218 2008-05-03 14:17:26Z ctheune $
"""

import time
import zope.testing.testrunner.feature


UNITTEST_LAYER = 'zope.testing.testrunner.layer.UnitTests'


class Filter(zope.testing.testrunner.feature.Feature):
    """Filters and orders all tests registered until now."""

    active = True

    def global_setup(self):
        layers = self.runner.tests_by_layer_name
        options = self.runner.options
        print 'Filtering ... ',

        if self.runner.options.resume_layer is not None:
            for name in list(layers):
                if name != self.runner.options.resume_layer:
                    layers.pop(name)
        elif self.runner.options.layer:
            for name in list(layers):
                for pat in self.runner.options.layer:
                    if pat(name):
                        # This layer matches a pattern selecting this layer
                        break
                else:
                    # No pattern matched this name so we remove it
                    layers.pop(name)

        amount = sum(t.countTestCases() for t in layers.values())
        print 'kept %s tests in %s layers' % (amount, len(layers))

    def report(self):
        if not self.runner.do_run_tests:
            return
        if self.runner.options.resume_layer:
            return
        if self.runner.options.verbose:
            print self.runner.errors
            print self.runner.failures
