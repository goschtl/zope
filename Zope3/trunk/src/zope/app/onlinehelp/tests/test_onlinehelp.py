##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Test OnlineHelp

$Id: test_onlinehelp.py,v 1.5 2003/09/21 17:32:31 jim Exp $
"""
import os
from unittest import TestSuite, makeSuite
from zope.component.adapter import provideAdapter
from zope.app.tests.placelesssetup import PlacelessSetup
from zope.interface import Interface
from zope.interface.verify import verifyObject
from zope.app.onlinehelp import OnlineHelp
from zope.app.interfaces.onlinehelp import IOnlineHelp
from zope.app.interfaces.traversing import ITraversable, IPhysicallyLocatable
from zope.app.interfaces.traversing import IContainmentRoot, ITraverser
from zope.app.location import LocationPhysicallyLocatable
from zope.app.traversing.adapters import Traverser, DefaultTraversable
from test_onlinehelptopic import TestOnlineHelpTopic, testdir

class I1(Interface):
    pass

class TestOnlineHelp(PlacelessSetup, TestOnlineHelpTopic):

    def setUp(self):
        PlacelessSetup.setUp(self)
        provideAdapter(None, ITraverser, Traverser)
        provideAdapter(None, ITraversable, DefaultTraversable)
        provideAdapter(None, IPhysicallyLocatable, LocationPhysicallyLocatable)
        path = os.path.join(testdir(), 'help.txt')
        self.topic = OnlineHelp('Help', path, 'txt')

    def test_registerHelpTopic(self):
        path = os.path.join(testdir(), 'help2.txt')
        self.topic.registerHelpTopic('', 'help2', 'Help 2',
                                     path, 'txt', I1, 'view.html')
        self.assertEqual(self.topic['help2'].title, 'Help 2')
        self.assertEqual(self.topic._registry[(I1, 'view.html')][0].title,
                         'Help 2')
        
    def test_getTopicsForInterfaceAndView(self):
        path = os.path.join(testdir(), 'help2.txt')
        self.topic.registerHelpTopic('', 'help2', 'Help 2',
                                     path, 'txt', I1, 'view.html')
        self.assertEqual(
            self.topic.getTopicsForInterfaceAndView(I1, 'view.html')[0].title,
            'Help 2')
            
    def test_interface(self):
        verifyObject(IOnlineHelp, self.topic)
        verifyObject(IContainmentRoot, self.topic)


def test_suite():
    return TestSuite((
        makeSuite(TestOnlineHelp),
        ))
