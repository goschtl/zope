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


class Filter(zope.testing.testrunner.feature.Feature):
    """Filters and orders all tests registered until now."""

    active = True

    def global_setup(self):
        tests = self.runner.tests_by_layer_name
        options = self.runner.options

        if 'unit' in tests:
            # We start out assuming unit tests should run and look for reasons
            # why they shouldn't be run.
            should_run = True
            if (not options.non_unit) and not options.resume_layer:
                if options.layer:
                    should_run = False
                    for pat in options.layer:
                        if pat('unit'):
                            should_run = True
                            break
                else:
                    should_run = True
            else:
                should_run = False

            if not should_run:
                tests.pop('unit')
