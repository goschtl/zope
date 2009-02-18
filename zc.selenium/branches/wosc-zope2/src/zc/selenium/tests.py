##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Test harness for zc.selenium.

$Id: tests.py 12897 2006-07-26 20:11:41Z fred $
"""

from zope.testing import doctest
import Queue
import time
import unittest
import urllib
import urllib2
import zc.selenium.http
import zc.selenium.pytest
import zc.selenium.selenium


class TestSelenium(zc.selenium.pytest.Test):
    """Selenium self-test."""

    def test_open(self):
        self.selenium.open('http://%s/' % self.selenium.server)
        # could be zope3 or zope2
        self.selenium.verifyTextPresent('regexp:Login|Zope Quick Start')


class HTTPTest(unittest.TestCase):

    def test_request(self):
        messages = zc.selenium.selenium.messages = Queue.Queue()
        s = zc.selenium.http.ServerThread(39589)
        s.start()
        time.sleep(1)
        params = dict(result='passed')
        response = urllib2.urlopen('http://localhost:39589/',
                                   urllib.urlencode(params))
        self.assertNotEqual(-1, response.read().find('Passed!'))
        self.assertEquals(params, messages.get(True))
        self.assertRaises(Queue.Empty, lambda: messages.get(False))


def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(HTTPTest),
        doctest.DocFileSuite('pytest.txt',
                    optionflags=doctest.ELLIPSIS|doctest.REPORT_NDIFF),
        doctest.DocTestSuite('zc.selenium.pytest'),
    ])
