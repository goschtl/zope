##############################################################################
#
# Copyright (c) 2001, 2002, 2009 Zope Foundation and Contributors.
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
"""Component Architecture Tests
"""
import unittest

from zope.interface import Interface
from zope.interface import implementer
from zope.interface.interfaces import IInterface

from zope.component.testfiles.views import IC

from zope.component.testing import setUp
from zope.component.testing import tearDown

# side effect gets component-based event dispatcher installed.
# we should obviously make this more explicit
import zope.component.event

class ITestType(IInterface):
    pass


class I1(Interface):
    pass

class I2(Interface):
    pass

class I3(Interface):
    pass

class I4(Interface):
    pass

class IGI(Interface):
    pass

class IQI(Interface):
    pass

class ISI(Interface):
    pass

class ISII(Interface):
    pass

def noop(*args):
    pass

@implementer(I1)
class Ob(object):
    def __repr__(self):
        return '<instance Ob>'


ob = Ob()

@implementer(I2)
class Ob2(object):
    def __repr__(self):
        return '<instance Ob2>'

@implementer(IC)
class Ob3(object):
    pass

@implementer(I2)
class Comp(object):
    def __init__(self, context):
        self.context = context

comp = Comp(1)

@implementer(I3)
class Comp2(object):
    def __init__(self, context):
        self.context = context


class ConformsToIComponentLookup(object):
    """Allow a dummy sitemanager to conform/adapt to `IComponentLookup`."""

    def __init__(self, sitemanager):
        self.sitemanager = sitemanager

    def __conform__(self, interface):
        """This method is specified by the adapter PEP to do the adaptation."""
        from zope.component.interfaces import IComponentLookup
        if interface is IComponentLookup:
            return self.sitemanager


class StandaloneTests(unittest.TestCase):
    def testStandalone(self):
        # See: https://bugs.launchpad.net/zope3/+bug/98401
        import subprocess
        import sys
        import os
        import pickle

        executable = os.path.abspath(sys.executable)
        where = os.path.dirname(os.path.dirname(__file__))
        program = os.path.join(where, 'standalonetests.py')
        process = subprocess.Popen([executable, program],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   stdin=subprocess.PIPE)
        pickle.dump(sys.path, process.stdin)
        process.stdin.close()

        try:
            rc = process.wait()
        except OSError, e:
            if e.errno != 4: # MacIntel raises apparently unimportant EINTR?
                raise # TODO verify sanity of a pass on EINTR :-/
        self.assertEqual(rc, 0)

def clearZCML(test=None):
    from zope.configuration.xmlconfig import XMLConfig
    import zope.component
    tearDown()
    setUp()
    XMLConfig('meta.zcml', zope.component)()

def test_suite():
    import doctest
    return unittest.TestSuite((
        doctest.DocTestSuite('zope.component.nexttesting'),
        unittest.makeSuite(StandaloneTests),
        ))
