##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Message Functional Tests

$Id$
"""
import unittest
from zope.app.tests.functional import BrowserTestCase

class MessageTest(BrowserTestCase):

    def testAddMessage(self):
        response = self.publish(
            '/+/AddMessageBoard.html=board',
            basic='mgr:mgrpw',
            form={'field.description': u'Message Board',
                  'UPDATE_SUBMIT': 'Add'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/@@contents.html')
        response = self.publish(
            '/board/+/AddMessage.html=msg1',
            basic='mgr:mgrpw',
            form={'field.title': u'Message 1',
                  'field.body': u'Body',
                  'UPDATE_SUBMIT': 'Add'})
        self.assertEqual(response.getStatus(), 302)
        self.assertEqual(response.getHeader('Location'),
                         'http://localhost/board/@@contents.html')
       
    def testMessageDetails(self):
        self.testAddMessage()
        response = self.publish('/board/msg1/@@details.html',
                                basic='mgr:mgrpw')
        body = response.getBody()
        self.checkForBrokenLinks(body, '/board/msg1/@@details.html',
                                 basic='mgr:mgrpw')
        
        self.assert_(body.find('Message Details') > 0)
        self.assert_(body.find('Message 1') > 0)
        self.assert_(body.find('Body') > 0)
        

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(MessageTest),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
