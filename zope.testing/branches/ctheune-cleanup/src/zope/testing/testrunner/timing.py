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
"""Timing support.

$Id: __init__.py 86218 2008-05-03 14:17:26Z ctheune $
"""

import time
import zope.testing.testrunner.feature


class Timing(zope.testing.testrunner.feature.Feature):

    active = True

    def late_setup(self):
        self.start_time = time.time()

    def early_teardown(self):
        self.end_time = time.time()

    def global_teardown(self):
        self.runner.total_time = self.end_time - self.start_time
