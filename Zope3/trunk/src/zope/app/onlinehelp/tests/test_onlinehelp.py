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

$Id: test_onlinehelp.py,v 1.1 2003/01/07 12:27:52 srichter Exp $
"""
import os
from unittest import TestSuite, makeSuite
from zope.interface import Interface
from zope.app.onlinehelp import OnlineHelp
from test_onlinehelptopic import TestOnlineHelpTopic, testdir

class I1(Interface):
    pass

class View:
    pass

class TestOnlineHelp(TestOnlineHelpTopic):

    def setUp(self):
        path = os.path.join(testdir(), 'help.txt')
        self.topic = OnlineHelp('Help', path, 'txt')

    def test_registerHelpTopic(self):
        path = os.path.join(testdir(), 'help2.txt')
        self.topic.registerHelpTopic('', 'help2', 'Help 2',
                                     path, 'txt', I1, View)
        self.assertEqual(self.topic['help2'].title, 'Help 2')
        self.assertEqual(self.topic._registry[(I1, View)][0].title, 'Help 2')

        # XXX: Needs CA setup
        #self.topic.unregisterHelpTopic('help2')
        #self.assertEqual(self.topic.get('help2', None), None)
        #self.assertEqual(self.topic._registry[(I1, View)], [])
        
    def test_getTopicsForInterfaceAndView(self):
        path = os.path.join(testdir(), 'help2.txt')
        self.topic.registerHelpTopic('', 'help2', 'Help 2',
                                     path, 'txt', I1, View)
        self.assertEqual(
            self.topic.getTopicsForInterfaceAndView(I1, View)[0].title,
            'Help 2')

def test_suite():
    return TestSuite((
        makeSuite(TestOnlineHelp),
        ))
