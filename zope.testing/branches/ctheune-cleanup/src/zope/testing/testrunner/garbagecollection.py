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
"""Garbage collection support.

$Id: __init__.py 86218 2008-05-03 14:17:26Z ctheune $
"""

import gc
import time
import zope.testing.testrunner.feature


class Threshold(zope.testing.testrunner.feature.Feature):

    def __init__(self, runner):
        super(Threshold, self).__init__(runner)
        self.threshold = self.runner.options.gc
        self.active = bool(self.threshold)

        if not self.active:
            return

        if len(self.threshold) > 3:
            output.error("Too many --gc options")
            sys.exit(1)

    def global_setup(self):
        self.old_threshold = gc.get_threshold()

        if self.threshold[0]:
            self.runner.options.output.info(
                "Cyclic garbage collection threshold set to: %s" %
                repr(tuple(self.threshold)))
        else:
            self.runner.options.output.info(
                "Cyclic garbage collection is disabled.")

        gc.set_threshold(*self.threshold)

    def global_teardown(self):
        gc.set_threshold(*self.old_threshold)
