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

$Id: test_onlinehelptopic.py,v 1.1 2003/01/07 12:27:52 srichter Exp $
"""
import os
from unittest import TestCase, TestSuite, makeSuite
from zope.app.onlinehelp import OnlineHelpTopic

def testdir():
    import zope.app.onlinehelp.tests
    return os.path.dirname(zope.app.onlinehelp.tests.__file__)

class TestOnlineHelpTopic(TestCase):

    def setUp(self):
        path = os.path.join(testdir(), 'help.txt')
        self.topic = OnlineHelpTopic('Help', path, 'txt')

    def test_title(self):
        self.assertEqual(self.topic.getTitle(), 'Help')
        self.assertEqual(self.topic.title, 'Help')
        self.topic.setTitle('Help1')
        self.assertEqual(self.topic.getTitle(), 'Help1')
        self.assertEqual(self.topic.title, 'Help1')
        self.topic.title = 'Help2'
        self.assertEqual(self.topic.getTitle(), 'Help2')
        self.assertEqual(self.topic.title, 'Help2')

    def test_content(self):
        self.assertEqual(self.topic.getContent(),
                         '<p>This is a help!</p>')
        path = os.path.join(testdir(), 'help.txt')
        self.topic.setContentPath(path, 'foo')
        self.assertEqual(self.topic.getContent(),
                         'This is a help!')

def test_suite():
    return TestSuite((
        makeSuite(TestOnlineHelpTopic),
        ))
