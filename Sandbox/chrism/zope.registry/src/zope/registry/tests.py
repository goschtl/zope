##############################################################################
#
# Copyright (c) 2001, 2002, 2009 Zope Corporation and Contributors.
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

$Id: tests.py 105528 2009-11-08 11:05:28Z kobold $
"""
import re
import unittest

from zope.testing.cleanup import cleanUp

from zope import interface
import zope.interface
from zope.registry import adapts
from zope.registry import adapter
from zope.interface.interfaces import IInterface
from zope.testing import doctest, renormalizing

from zope.registry.interfaces import IComponentLookup

from zope.registry.testfiles.adapter import A1, A2, A3
from zope.registry.testfiles.components import IContent, Content
from zope.registry.testfiles.components import IApp
from zope.registry.testfiles.views import Request, IC, IV, V1, R1, IR

# side effect gets component-based event dispatcher installed.
# we should obviously make this more explicit
# import zope.component.event

class I1(interface.Interface):
    pass
class I2(interface.Interface):
    pass
class I2e(I2):
    pass
class I3(interface.Interface):
    pass

class ITestType(IInterface):
    pass

class U:

    def __init__(self, name):
        self.__name__ = name

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.__name__)

class U1(U):
    interface.implements(I1)

class U12(U):
    interface.implements(I1, I2)

class IA1(interface.Interface):
    pass

class IA2(interface.Interface):
    pass

class IA3(interface.Interface):
    pass

class A:

    def __init__(self, *context):
        self.context = context

    def __repr__(self):
        return "%s%r" % (self.__class__.__name__, self.context)

class A12_1(A):
    adapts(I1, I2)
    interface.implements(IA1)

class A12_(A):
    adapts(I1, I2)

class A_2(A):
    interface.implements(IA2)

class A_3(A):
    interface.implements(IA3)

class A1_12(U):
    adapts(I1)
    interface.implements(IA1, IA2)

class A1_2(U):
    adapts(I1)
    interface.implements(IA2)

class A1_23(U):
    adapts(I1)
    interface.implements(IA1, IA3)

def noop(*args):
    pass

@adapter(I1)
def handle1(x):
    print 'handle1', x

def handle(*objects):
    print 'handle', objects

@adapter(I1)
def handle3(x):
    print 'handle3', x

@adapter(I1)
def handle4(x):
    print 'handle4', x

class Ob(object):
    interface.implements(I1)
    def __repr__(self):
        return '<instance Ob>'


ob = Ob()

class Ob2(object):
    interface.implements(I2)
    def __repr__(self):
        return '<instance Ob2>'

class Comp(object):
    interface.implements(I2)
    def __init__(self, context):
        self.context = context

comp = Comp(1)

class Comp2(object):
    interface.implements(I3)
    def __init__(self, context):
        self.context = context


class ConformsToIComponentLookup(object):
    """This object allows the sitemanager to conform/adapt to
    `IComponentLookup` and thus to itself."""

    def __init__(self, sitemanager):
        self.sitemanager = sitemanager

    def __conform__(self, interface):
        """This method is specified by the adapter PEP to do the adaptation."""
        if interface is IComponentLookup:
            return self.sitemanager


def testNo__component_adapts__leakage():
    """
    We want to make sure that an `adapts()` call in a class definition
    doesn't affect instances.

      >>> class C:
      ...     adapts()

      >>> C.__component_adapts__
      ()
      >>> C().__component_adapts__
      Traceback (most recent call last):
      ...
      AttributeError: __component_adapts__
    """

def test_multi_handler_unregistration():
    """
    There was a bug where multiple handlers for the same required
    specification would all be removed when one of them was
    unregistered:

    >>> class I(zope.interface.Interface):
    ...     pass
    >>> def factory1(event):
    ...     print "| Factory 1 is here"
    >>> def factory2(event):
    ...     print "| Factory 2 is here"
    >>> class Event(object):
    ...     zope.interface.implements(I)
    >>> from zope.registry import Components
    >>> registry = Components()
    >>> registry.registerHandler(factory1, [I,])
    >>> registry.registerHandler(factory2, [I,])
    >>> registry.handle(Event())
    | Factory 1 is here
    | Factory 2 is here
    >>> registry.unregisterHandler(factory1, [I,])
    True
    >>> registry.handle(Event())
    | Factory 2 is here
    """


def dont_leak_utility_registrations_in__subscribers():
    """

    We've observed utilities getting left in _subscribers when they
    get unregistered.

    >>> import zope.registry
    >>> reg = zope.registry.Components()
    >>> class C:
    ...     def __init__(self, name):
    ...         self.name = name
    ...     def __repr__(self):
    ...         return "C(%s)" % self.name

    >>> c1 = C(1)
    >>> reg.registerUtility(c1, I1)
    >>> reg.registerUtility(c1, I1)
    >>> list(reg.getAllUtilitiesRegisteredFor(I1))
    [C(1)]

    >>> reg.unregisterUtility(provided=I1)
    True
    >>> list(reg.getAllUtilitiesRegisteredFor(I1))
    []

    >>> reg.registerUtility(c1, I1)
    >>> reg.registerUtility(C(2), I1)

    >>> list(reg.getAllUtilitiesRegisteredFor(I1))
    [C(2)]

    """

class Ob3(object):
    interface.implements(IC)

template = """<configure
   xmlns='http://namespaces.zope.org/zope'
   i18n_domain='zope'>
   %s
   </configure>"""


def setUpRegistryTests(tests):
    cleanUp()

def tearDownRegistryTests(tests):
    cleanUp()
    import zope.event
    zope.event.subscribers.pop()

def setUp(test=None):
    cleanUp()

def tearDown(test=None):
    cleanUp()

def test_suite():
    checker = renormalizing.RENormalizing([
        (re.compile('at 0x[0-9a-fA-F]+'), 'at <SOME ADDRESS>'),
        (re.compile(r"<type 'exceptions.(\w+)Error'>:"),
                    r'exceptions.\1Error:'),
        ])

    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('registry.txt', checker=checker,
                             setUp=setUpRegistryTests,
                             tearDown=tearDownRegistryTests),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')
