##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

from pprint import pprint
import unittest

from zope.component.view import viewService
from zope.interface import Interface

from zope.testing.doctestunit import DocTestSuite

class R1(Interface):
    pass

class R12(R1):
    pass

class P1(Interface):
    pass

class Factory:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "Factory(%r)" % self.name

    def __call__(self):
        return

def getRegisteredMatching(**kwargs):
    L = viewService.getRegisteredMatching(**kwargs)
    return pprint([(r.__name__, p.__name__, f, l, n)
                   for r, p, f, l, n in L])

def test_getRegisteredMatching():
    """Try various combinations of arguments to getRegisteredMatching().

    First setup a couple of views.
    
    >>> chain = [Factory("shoe")]
    >>> chain2 = [Factory("glue")]
    >>> viewService.provideView(R1, "Bowser", P1, chain)
    >>> viewService.provideView(R12, "Bowser", P1, chain2)

    Start the tests.
    
    >>> getRegisteredMatching(required_interfaces=[R1])
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(required_interfaces=[R12])
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser'),
     ('R12', 'P1', [Factory('glue')], 'default', 'Bowser')]
    >>> getRegisteredMatching(required_interfaces=[P1])
    []
    >>> getRegisteredMatching(presentation_type=P1)
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser'),
     ('R12', 'P1', [Factory('glue')], 'default', 'Bowser')]
    >>> getRegisteredMatching(presentation_type=R1)
    []
    >>> getRegisteredMatching(required_interfaces=[R1], presentation_type=P1)
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(required_interfaces=[R12], presentation_type=P1)
    [('R12', 'P1', [Factory('glue')], 'default', 'Bowser'),
     ('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(required_interfaces=[P1], presentation_type=P1)
    []
    >>> getRegisteredMatching(viewName="Bowser")
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser'),
     ('R12', 'P1', [Factory('glue')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Bowser", required_interfaces=[R1])
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Bowser", required_interfaces=[R12])
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser'),
     ('R12', 'P1', [Factory('glue')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Bowser", required_interfaces=[R12],
    ...                       presentation_type=P1)
    [('R12', 'P1', [Factory('glue')], 'default', 'Bowser'),
     ('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Bowser", required_interfaces=[R1],
    ...                       presentation_type=P1)
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Yoshi", required_interfaces=[R1],
    ...                       presentation_type=P1)
    []
    >>> getRegisteredMatching(layer=1)
    []
    >>> getRegisteredMatching(layer="default")
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser'),
     ('R12', 'P1', [Factory('glue')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Bowser", required_interfaces=[R1],
    ...                       presentation_type=P1, layer="default")
    [('R1', 'P1', [Factory('shoe')], 'default', 'Bowser')]
    >>> getRegisteredMatching(viewName="Bowser", required_interfaces=[R1],
    ...                       presentation_type=P1, layer="Default")
    []

    >>> viewService._clear()
    """

def test_suite():
    return DocTestSuite()
