#!/usr/bin/python
"""
Unit tests for message.py

$Id$
"""

import unittest
from datetime import datetime
from zope.interface.verify import verifyObject
from zope.app.container.interfaces import IContainerNamesContainer
from z3checkins.interfaces import ICheckinFolder


class TestCheckinFolder(unittest.TestCase):

    def test_folder(self):
        from z3checkins.folder import CheckinFolder
        folder = CheckinFolder()
        verifyObject(ICheckinFolder, folder)
        verifyObject(IContainerNamesContainer, folder)
        self.assertEquals(folder.messages, [])

    def test_index(self):
        from z3checkins.folder import CheckinFolder
        from z3checkins.message import Message

        folder = CheckinFolder()
        folder['msg1'] = Message(date=datetime(2004, 1, 2, 3, 4))
        folder['msg2'] = Message(date=datetime(2005, 1, 5, 7, 8))
        folder['msg3'] = Message(date=datetime(2004, 7, 5, 7, 8))
        folder['msg4'] = Message(date=datetime(2004, 3, 5, 7, 8))
        folder['bogus'] = "not a message"
        folder['bogus2'] = 17

        self.assertEquals([msg.__name__ for msg in folder.messages],
                          ['msg2', 'msg3', 'msg4', 'msg1'])

        folder['msg5'] = Message(date=datetime(2004, 5, 1, 2, 3))
        self.assertEquals([msg.__name__ for msg in folder.messages],
                          ['msg2', 'msg3', 'msg5', 'msg4', 'msg1'])

        # test delete index
        del folder['msg3']
        self.assertEquals([msg.__name__ for msg in folder.messages],
                          ['msg2', 'msg5', 'msg4', 'msg1'])

        del folder['bogus']
        del folder['bogus2']
        self.assertEquals([msg.__name__ for msg in folder.messages],
                          ['msg2', 'msg5', 'msg4', 'msg1'])


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCheckinFolder))
    return suite


if __name__ == "__main__":
    unittest.main()

