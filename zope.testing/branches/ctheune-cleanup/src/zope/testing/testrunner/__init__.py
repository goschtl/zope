##############################################################################
#
# Copyright (c) 2004-2006 Zope Corporation and Contributors.
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
"""Test runner

$Id$
"""

import gc
import glob
import logging
import os
import errno
import pdb
import re
import cStringIO
import sys
import tempfile
import threading
import time
import trace
import traceback
import types
import unittest


from zope.testing import doctest
from zope.testing.testrunner.formatter import OutputFormatter, ColorfulOutputFormatter
from zope.testing.testrunner.formatter import terminal_has_colors
from zope.testing.testrunner.find import name_from_layer, _layer_name_cache
from zope.testing.testrunner.runner import run, EndRun


class TrackRefs(object):
    """Object to track reference counts across test runs."""

    def __init__(self):
        self.type2count = {}
        self.type2all = {}
        self.delta = None
        self.n = 0
        self.update()
        self.delta = None

    def update(self):
        gc.collect()
        obs = sys.getobjects(0)
        type2count = {}
        type2all = {}
        n = 0
        for o in obs:
            if type(o) is str and o == '<dummy key>':
                # avoid dictionary madness
                continue

            all = sys.getrefcount(o) - 3
            n += all

            t = type(o)
            if t is types.InstanceType:
                t = o.__class__

            if t in type2count:
                type2count[t] += 1
                type2all[t] += all
            else:
                type2count[t] = 1
                type2all[t] = all


        ct = [(
               type_or_class_title(t),
               type2count[t] - self.type2count.get(t, 0),
               type2all[t] - self.type2all.get(t, 0),
               )
              for t in type2count.iterkeys()]
        ct += [(
                type_or_class_title(t),
                - self.type2count[t],
                - self.type2all[t],
                )
               for t in self.type2count.iterkeys()
               if t not in type2count]
        ct.sort()
        self.delta = ct
        self.type2count = type2count
        self.type2all = type2all
        self.n = n


    def output(self):
        printed = False
        s1 = s2 = 0
        for t, delta1, delta2 in self.delta:
            if delta1 or delta2:
                if not printed:
                    print (
                        '    Leak details, changes in instances and refcounts'
                        ' by type/class:')
                    print "    %-55s %6s %6s" % ('type/class', 'insts', 'refs')
                    print "    %-55s %6s %6s" % ('-' * 55, '-----', '----')
                    printed = True
                print "    %-55s %6d %6d" % (t, delta1, delta2)
                s1 += delta1
                s2 += delta2

        if printed:
            print "    %-55s %6s %6s" % ('-' * 55, '-----', '----')
            print "    %-55s %6s %6s" % ('total', s1, s2)


        self.delta = None


def type_or_class_title(t):
    module = getattr(t, '__module__', '__builtin__')
    if module == '__builtin__':
        return t.__name__
    return "%s.%s" % (module, t.__name__)


###############################################################################
# Install 2.4 TestSuite __iter__ into earlier versions

if sys.version_info < (2, 4):
    def __iter__(suite):
        return iter(suite._tests)
    unittest.TestSuite.__iter__ = __iter__
    del __iter__

# Install 2.4 TestSuite __iter__ into earlier versions
###############################################################################
