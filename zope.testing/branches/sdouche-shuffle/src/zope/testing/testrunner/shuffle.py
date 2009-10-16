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
"""Shuffle tests discovered before executing them.

$Id$
"""

import time
import random
import unittest
import zope.testing.testrunner.feature


class Shuffle(zope.testing.testrunner.feature.Feature):
    """Shuffle tests found."""

    def __init__(self, runner):
        super(Shuffle, self).__init__(runner)
        self.active = runner.options.shuffle

        self.seed = runner.options.shuffle_seed
        if self.seed is None:
            # Imported from stdlib's random.py
            # This is not the best way to obtain a random value, but in our
            # case, this is very sufficient.
            self.seed = long(time.time() * 256) # use fractional seconds

    def global_setup(self):
        shuffler = random.Random(self.seed)

        # Recreate the list of tests and shuffle them
        shuffled_tests = {}
        for layer_name, tests in self.runner.tests_by_layer_name.iteritems():
            tests = list(tests) # Make a copy
            shuffler.shuffle(tests)
            shuffled_tests[layer_name] = unittest.TestSuite(tests)

        self.runner.tests_by_layer_name = shuffled_tests

    def report(self):
        msg = "Tests were shuffled using seed number %d" % self.seed
        self.runner.options.output.info(msg)
