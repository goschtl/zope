##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""

$Id$
"""

import unittest
from zope.server.http.httprequestparser import HTTPRequestParser
from zope.server.adjustments import Adjustments


my_adj = Adjustments()

class Tests(unittest.TestCase):

    def setUp(self):
        self.parser = HTTPRequestParser(my_adj)

    def feed(self, data):
        parser = self.parser
        for n in xrange(100): # make sure we never loop forever
            consumed = parser.received(data)
            data = data[consumed:]
            if parser.completed:
                return
        raise ValueError, 'Looping'

    def testSimpleGET(self):
        data = """\
GET /foobar HTTP/8.4
FirstName: mickey
lastname: Mouse
content-length: 7

Hello.
"""
        parser = self.parser
        self.feed(data)
        self.failUnless(parser.completed)
        self.assertEqual(parser.version, '8.4')
        self.failIf(parser.empty)
        self.assertEqual(parser.headers,
                         {'FIRSTNAME': 'mickey',
                          'LASTNAME': 'Mouse',
                          'CONTENT_LENGTH': '7',
                          })
        self.assertEqual(parser.path, '/foobar')
        self.assertEqual(parser.command, 'GET')
        self.assertEqual(parser.query, None)
        self.assertEqual(parser.getBodyStream().getvalue(), 'Hello.\n')

    def testComplexGET(self):
        data = """\
GET /foo/a+%2B%2F%3D%26a%3Aint?d=b+%2B%2F%3D%26b%3Aint&c+%2B%2F%3D%26c%3Aint=6 HTTP/8.4
FirstName: mickey
lastname: Mouse
content-length: 10

Hello mickey.
"""
        parser = self.parser
        self.feed(data)
        self.assertEqual(parser.command, 'GET')
        self.assertEqual(parser.version, '8.4')
        self.failIf(parser.empty)
        self.assertEqual(parser.headers,
                         {'FIRSTNAME': 'mickey',
                          'LASTNAME': 'Mouse',
                          'CONTENT_LENGTH': '10',
                          })
        self.assertEqual(parser.path, '/foo/a++/=&a:int')
        self.assertEqual(parser.query, 'd=b+%2B%2F%3D%26b%3Aint&c+%2B%2F%3D%26c%3Aint=6')
        self.assertEqual(parser.getBodyStream().getvalue(), 'Hello mick')


def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(Tests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
