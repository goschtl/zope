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
"""Tests for the useconfiguration view support."""

import unittest

from zope.app.browser.services.utility import useconfiguration
from zope.app.tests import placelesssetup
from zope.component.view import provideView
from zope.interface import Interface
from zope.publisher.browser import BrowserView, IBrowserPresentation
from zope.publisher.browser import TestRequest


class IFoo(Interface):
    """Sample interface."""
    def someMethod(someArg):
        """Sample interface method."""

class IBar(IFoo):
    """Derived interface."""
    def anotherMethod():
        """Another example method interface."""

class IStub(Interface):
    """Interface used to bind an absolute_url view to stub objects."""

class Stub:
    # Does triple duty as a stub for a configuration, a configuration
    # registry, and a component!

    __implements__ = IStub

    def __init__(self, url=None):
        self.url = url

    # configuration registry
    def active(self):
        if self.url:
            return self
        else:
            return None

    # configuration
    def getComponent(self):
        return self

class StubAbsoluteURL(BrowserView):
    def __str__(self):
        return self.context.url

class StubLocalUtilityService:
    def getRegisteredMatching(self):
        return [
            # (iface, name, configregistry)
            (IFoo, '', Stub("1")),
            (IFoo, 'myfoo-1', Stub("2")),
            (IFoo, 'myfoo-2', Stub()),
            (IBar, '', Stub()),
            (IBar, 'mybar-1', Stub("3"))
            ]


class UseConfigurationTest(placelesssetup.PlacelessSetup, unittest.TestCase):

    def test_utility(self):
        provideView(IStub,
                    "absolute_url",
                    IBrowserPresentation,
                    StubAbsoluteURL)
        utilityservice = StubLocalUtilityService()
        request = TestRequest()
        utilities = useconfiguration.Utilities(utilityservice, request)
        ifname1 = __name__ + ".IFoo"
        ifname2 = __name__ + ".IBar"
        def confurl(ifname, name):
            return ("@@configureutility.html?interface=%s&name=%s"
                    % (ifname, name))
        expected = [{"interface": ifname2,
                     "name": "",
                     "url": "",
                     "configurl": confurl(ifname2, '')},
                    {"interface": ifname2,
                     "name": "mybar-1",
                     "url": "3",
                     "configurl": confurl(ifname2, 'mybar-1')},
                    {"interface": ifname1,
                     "name": "",
                     "url": "1",
                     "configurl": confurl(ifname1, '')},
                    {"interface": ifname1,
                     "name": "myfoo-1",
                     "url": "2",
                     "configurl": confurl(ifname1, 'myfoo-1')},
                    {"interface": ifname1,
                     "name": "myfoo-2",
                     "url": "",
                     "configurl": confurl(ifname1, 'myfoo-2')},
                    ]
        result = utilities.getConfigs()
        self.assertEqual(len(expected), len(result))
        for r, e in zip(result, expected):
            ri = r.items()
            ri.sort()
            ei = e.items()
            ei.sort()
            self.assertEqual(ri, ei)


def test_suite():
    return unittest.makeSuite(UseConfigurationTest)
