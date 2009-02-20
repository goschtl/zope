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


class Zope3Test(zc.selenium.pytest.Test):
    def test_open(self):
        self.selenium.open('/')
        self.selenium.verifyTextPresent('Login')

    # XXX missing
#     def test_add_foo(self)

#     # should work because of zc.selenium's DemoStorage-Stack
#     def test_add_foo_again(self):
#         self.test_add_foo()

# Zope2 requires docstrings on views
class Zope2Test(zc.selenium.pytest.Test):
    """Selenium self-test."""

    def test_open(self):
        self.selenium.open('/')
        self.selenium.verifyTextPresent('Zope Quick Start')

    def test_add_foo(self):
        s = self.selenium
        s.open('http://admin:admin@%s/manage' % self.selenium.server)
        # XXX: I wish we had some ids to go on...
        s.select('//form[@method="get"]/select[@name=":action"]', 'Folder')
        s.type('name=id', 'foo')
        s.click('//input[@value="Add"]')
        s.verifyTextNotPresent('it is already in use')
        s.waitForElementPresent('link=foo')

    # should work because of zc.selenium's DemoStorage-Stack
    def test_add_foo_again(self):
        self.test_add_foo()


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
