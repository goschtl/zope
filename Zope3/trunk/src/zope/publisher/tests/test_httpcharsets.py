##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Retrieval of HTTP character set information.

$Id: test_httpcharsets.py,v 1.2 2002/12/25 14:15:19 jim Exp $
"""
import unittest, sys

from zope.publisher.http import HTTPCharsets


class HTTPCharsetTest(unittest.TestCase):

    def testGetPreferredCharset(self):
        request = {'HTTP_ACCEPT_CHARSET':
                   'ISO-8859-1, UTF-8;q=0.66, UTF-16;q=0.33'}
        browser_charsets = HTTPCharsets(request)
        self.assertEqual(list(browser_charsets.getPreferredCharsets()),
                         ['utf-8', 'iso-8859-1', 'utf-16'])

    def testGetPreferredCharsetOrdering(self):
        # test that the charsets are returned sorted according to
        # their "quality value"
        request = {'HTTP_ACCEPT_CHARSET':
                   'ISO-8859-1, UTF-16;Q=0.33, UTF-8;q=0.66'}
        browser_charsets = HTTPCharsets(request)
        self.assertEqual(list(browser_charsets.getPreferredCharsets()),
                         ['utf-8', 'iso-8859-1', 'utf-16'])

    def testGetPreferredCharsetBogusQuality(self):
        # test that handling of bogus "quality values" and non-quality
        # parameters is reasonable
        request = {'HTTP_ACCEPT_CHARSET':
                   'ISO-8859-1;x, UTF-16;Q=0.33, UTF-8;q=foo'}
        browser_charsets = HTTPCharsets(request)
        self.assertEqual(list(browser_charsets.getPreferredCharsets()),
                         ['iso-8859-1', 'utf-16'])

    def testNoStar(self):
        request = {'HTTP_ACCEPT_CHARSET': 'utf-16;q=0.66'}
        browser_charsets = HTTPCharsets(request)
        self.assertEqual(list(browser_charsets.getPreferredCharsets()),
                         ['iso-8859-1', 'utf-16'])


def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(HTTPCharsetTest)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
