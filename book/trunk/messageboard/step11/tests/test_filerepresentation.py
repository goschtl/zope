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
"""FTP Views for the MessageBoard and Message component

$Id$
"""
import unittest
from zope.interface.verify import verifyObject
from zope.app import zapi
from zope.app.tests import ztapi
from zope.app.tests.placelesssetup import PlacelessSetup

from book.messageboard.interfaces import \
     IVirtualContentsFile, IPlainText, IMessage, IMessageBoard
from book.messageboard.message import \
     Message, PlainText as MessagePlainText
from book.messageboard.messageboard import \
     MessageBoard, PlainText as MessageBoardPlainText
from book.messageboard.filerepresentation import VirtualContentsFile
from book.messageboard.filerepresentation import ReadDirectory

class VirtualContentsFileTestBase(PlacelessSetup):

    def _makeFile(self):
        raise NotImplemented

    def _registerPlainTextAdapter(self):
        raise NotImplemented

    def setUp(self):
        PlacelessSetup.setUp(self)
        self._registerPlainTextAdapter()

    def testContentType(self):
        file = self._makeFile()
        self.assertEqual(file.getContentType(), 'text/plain')
        file.setContentType('text/html')
        self.assertEqual(file.getContentType(), 'text/plain')
        self.assertEqual(file.contentType, 'text/plain')

    def testData(self):
        file = self._makeFile()

        file.setData('Foobar')
        self.assert_(file.getData().find('Foobar') >= 0)
        self.assert_(file.data.find('Foobar') >= 0)

        file.edit('Blah', 'text/html')
        self.assertEqual(file.contentType, 'text/plain')
        self.assert_(file.data.find('Blah') >= 0)

    def testInterface(self):
        file = self._makeFile()
        self.failUnless(IVirtualContentsFile.providedBy(file))
        self.failUnless(verifyObject(IVirtualContentsFile, file))


class MessageVirtualContentsFileTest(VirtualContentsFileTestBase,
                                     unittest.TestCase):
    
    def _makeFile(self):
        return VirtualContentsFile(Message())

    def _registerPlainTextAdapter(self):
        ztapi.provideAdapter(IMessage, IPlainText, MessagePlainText)

    def testMessageSpecifics(self):
        file = self._makeFile()
        self.assertEqual(file.context.title, '')
        self.assertEqual(file.context.body, '')
        file.data = 'Title: Hello\n\nWorld'
        self.assertEqual(file.context.title, 'Hello')
        self.assertEqual(file.context.body, 'World')
        file.data = 'World 2'
        self.assertEqual(file.context.body, 'World 2')


class MessageBoardVirtualContentsFileTest(
      VirtualContentsFileTestBase, unittest.TestCase):
    
    def _makeFile(self):
        return VirtualContentsFile(MessageBoard())

    def _registerPlainTextAdapter(self):
        ztapi.provideAdapter(IMessageBoard, IPlainText, 
                             MessageBoardPlainText)

    def testMessageBoardSpecifics(self):
        file = self._makeFile()
        self.assertEqual(file.context.description, '')
        file.data = 'Title: Hello\n\nWorld'
        self.assertEqual(file.context.description, 
                         'Title: Hello\n\nWorld')
        file.data = 'World 2'
        self.assertEqual(file.context.description, 'World 2')


class ReadDirectoryTestBase(PlacelessSetup):

    def _makeDirectoryObject(self):
        raise NotImplemented

    def _makeTree(self):
        base = self._makeDirectoryObject()
        msg1 = Message()
        msg1.title = 'Message 1'
        msg1.description = 'This is Message 1.'
        msg11 = Message()
        msg11.title = 'Message 1-1'
        msg11.description = 'This is Message 1-1.'
        msg2 = Message()
        msg2.title = 'Message 1'
        msg2.description = 'This is Message 1.'
        msg1['msg11'] = msg11
        base['msg1'] = msg1
        base['msg2'] = msg2
        return ReadDirectory(base)

    def testKeys(self):
        tree = self._makeTree()
        keys = list(tree.keys())
        keys.sort()
        self.assertEqual(keys, ['contents', 'msg1', 'msg2'])
        keys = list(ReadDirectory(tree['msg1']).keys())
        keys.sort()
        self.assertEqual(keys, ['contents', 'msg11'])

    def testGet(self):
        tree = self._makeTree()
        self.assertEqual(tree.get('msg1'), tree.context['msg1'])
        self.assertEqual(tree.get('msg3'), None)
        default = object()
        self.assertEqual(tree.get('msg3', default), default)
        self.assertEqual(tree.get('contents').__class__, 
                         VirtualContentsFile)

    def testLen(self):
        tree = self._makeTree()
        self.assertEqual(len(tree), 3)
        self.assertEqual(len(ReadDirectory(tree['msg1'])), 2)
        self.assertEqual(len(ReadDirectory(tree['msg2'])), 1)
        

class MessageReadDirectoryTest(ReadDirectoryTestBase, 
                               unittest.TestCase):

    def _makeDirectoryObject(self):
        return Message()


class MessageBoardReadDirectoryTest(ReadDirectoryTestBase, 
                                    unittest.TestCase):

    def _makeDirectoryObject(self):
        return MessageBoard()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MessageVirtualContentsFileTest),
        unittest.makeSuite(MessageBoardVirtualContentsFileTest),
        unittest.makeSuite(MessageReadDirectoryTest),
        unittest.makeSuite(MessageBoardReadDirectoryTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
