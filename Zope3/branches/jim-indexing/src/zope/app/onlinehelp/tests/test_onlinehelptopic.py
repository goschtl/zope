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
"""Test OnlineHelpTopic

$Id$
"""
import os
from unittest import TestCase, TestSuite, makeSuite
from zope.interface.verify import verifyObject
from zope.app.onlinehelp import OnlineHelpTopic, IOnlineHelpTopic

def testdir():
    import zope.app.onlinehelp.tests
    return os.path.dirname(zope.app.onlinehelp.tests.__file__)

class TestOnlineHelpTopic(TestCase):

    def setUp(self):
        path = os.path.join(testdir(), 'help.txt')
        self.topic = OnlineHelpTopic('Help', path, 'txt')

    def test_title(self):
        self.assertEqual(self.topic.title, 'Help')
        self.topic.title = 'Help1'
        self.assertEqual(self.topic.title, 'Help1')
        self.topic.title = 'Help2'
        self.assertEqual(self.topic.title, 'Help2')

    def test_content(self):
        self.assertEqual(self.topic.getContent(),
                         '<p>This is a help!</p>')
        path = os.path.join(testdir(), 'help.txt')
        self.topic.setContentPath(path, 'foo')
        self.assertEqual(self.topic.getContent(),
                         'This is a help!')
                         
    def test_interface(self):
        verifyObject(IOnlineHelpTopic, self.topic)
              

def test_suite():
    return TestSuite((
        makeSuite(TestOnlineHelpTopic),
        ))
