##############################################################################
#
# Copyright (c) 2003, 2004 Zope Corporation and Contributors.
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
"""XML-RPC Representation Tests

$Id$
"""
import unittest

from zope.publisher.xmlrpc import TestRequest

from zope.app.tests.placelesssetup import PlacelessSetup
from zope.app import zapi

from book.messageboard.message import Message
from book.messageboard.messageboard import MessageBoard
from book.messageboard.xmlrpc import MessageBoardMethods, MessageMethods

class MessageContainerTest(PlacelessSetup):

    def _makeMethodObject(self):
        return NotImplemented

    def _makeTree(self):
        methods = self._makeMethodObject()
        msg1 = Message()
        msg1.title = 'Message 1'
        msg1.description = 'This is Message 1.'
        msg2 = Message()
        msg2.title = 'Message 1'
        msg2.description = 'This is Message 1.'
        methods.context['msg1'] = msg1
        methods.context['msg2'] = msg2
        return methods

    def test_getMessageNames(self):
        methods = self._makeTree()
        self.assert_(isinstance(methods.getMessageNames(), list))
        self.assertEqual(list(methods.context.keys()),
                         methods.getMessageNames())

    def test_addMessage(self):
        methods = self._makeTree()
        self.assertEqual(methods.addMessage('msg3', 'M3', 'MB3'), 'msg3')
        self.assertEqual(methods.context['msg3'].title, 'M3')
        self.assertEqual(methods.context['msg3'].body, 'MB3')

    def test_deleteMessage(self):
        methods = self._makeTree()
        self.assertEqual(methods.deleteMessage('msg2'), True)
        self.assertEqual(list(methods.context.keys()), ['msg1'])


class MessageBoardMethodsTest(MessageContainerTest, unittest.TestCase):

    def _makeMethodObject(self):
        return MessageBoardMethods(MessageBoard(), TestRequest())

    def test_description(self):
        methods = self._makeTree()
        self.assertEqual(methods.getDescription(), '')
        self.assertEqual(methods.setDescription('Board 1') , True)
        self.assertEqual(methods.getDescription(), 'Board 1')


class MessageMethodsTest(MessageContainerTest, unittest.TestCase):

    def _makeMethodObject(self):
        return MessageMethods(Message(), TestRequest())

    def test_title(self):
        methods = self._makeTree()
        self.assertEqual(methods.getTitle(), '')
        self.assertEqual(methods.setTitle('Message 1') , True)
        self.assertEqual(methods.getTitle(), 'Message 1')

    def test_body(self):
        methods = self._makeTree()
        self.assertEqual(methods.getBody(), '')
        self.assertEqual(methods.setBody('Body 1') , True)
        self.assertEqual(methods.getBody(), 'Body 1')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MessageBoardMethodsTest),
        unittest.makeSuite(MessageMethodsTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
