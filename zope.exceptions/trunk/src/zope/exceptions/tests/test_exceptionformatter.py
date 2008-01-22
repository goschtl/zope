##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""ExceptionFormatter tests.

$Id$
"""
import sys
import unittest
import zope.testing.doctest

import zope.exceptions.log
from zope.exceptions.exceptionformatter import format_exception
from zope.testing.cleanup import CleanUp # Base class w registry cleanup
import logging
import StringIO

def tb(as_html=0, format=None):
    log = logging.getLogger('')
    fake_stdout = StringIO.StringIO()
    hndler = logging.StreamHandler(fake_stdout)
    hndler.setFormatter(zope.exceptions.log.Formatter(as_html=as_html, fmt=format))
    log.addHandler(hndler)

    t, v, b = sys.exc_info()
    try:
        log.exception('')
        s = fake_stdout.getvalue()
        return s
    finally:
        del b
        log.removeHandler(hndler)

class ExceptionForTesting (Exception):
    pass



class TestingTracebackSupplement(object):

    source_url = '/somepath'
    line = 634
    column = 57
    warnings = ['Repent, for the end is nigh']

    def __init__(self, expression):
        self.expression = expression



class Test(CleanUp, unittest.TestCase):

    def testBasicNamesText(self, as_html=0):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb(as_html)
            # The traceback should include the name of this function.
            self.assert_(s.find('testBasicNamesText') >= 0)
            # The traceback should include the name of the exception.
            self.assert_(s.find('ExceptionForTesting') >= 0)
        else:
            self.fail('no exception occurred')

    def testBasicNamesHTML(self):
        self.testBasicNamesText(1)

    def testSupplement(self, as_html=0):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb(as_html)
            # The source URL
            self.assert_(s.find('/somepath') >= 0, s)
            # The line number
            self.assert_(s.find('634') >= 0, s)
            # The column number
            self.assert_(s.find('57') >= 0, s)
            # The expression
            self.assert_(s.find("You're one in a million") >= 0, s)
            # The warning
            self.assert_(s.find("Repent, for the end is nigh") >= 0, s)
        else:
            self.fail('no exception occurred')

    def testSupplementHTML(self):
        self.testSupplement(1)

    def testTracebackInfo(self, as_html=0):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb(as_html)
            if as_html:
                # Be sure quoting is happening.
                self.assert_(s.find('Adam &amp; Eve') >= 0, s)
            else:
                self.assert_(s.find('Adam & Eve') >= 0, s)
        else:
            self.fail('no exception occurred')

    def testTracebackInfoHTML(self):
        self.testTracebackInfo(1)

    def testTracebackInfoTuple(self):
        try:
            __traceback_info__ = ("Adam", "Eve")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb()
            self.assert_(s.find('Adam') >= 0, s)
            self.assert_(s.find('Eve') >= 0, s)
        else:
            self.fail('no exception occurred')

    def testMultipleLevels(self):
        # Makes sure many levels are shown in a traceback.
        def f(n):
            """Produces a (n + 1)-level traceback."""
            __traceback_info__ = 'level%d' % n
            if n > 0:
                f(n - 1)
            else:
                raise ExceptionForTesting

        try:
            f(10)
        except ExceptionForTesting:
            s = tb()
            for n in range(11):
                self.assert_(s.find('level%d' % n) >= 0, s)
        else:
            self.fail('no exception occurred')

    def testQuoteLastLine(self):
        class C(object): pass
        try: raise TypeError(C())
        except:
            s = tb(1)
        else:
            self.fail('no exception occurred')
        self.assert_(s.find('&lt;') >= 0, s)
        self.assert_(s.find('&gt;') >= 0, s)

    def testMultilineException(self):
        try:
            exec 'syntax error'
        except:
            s = tb()
        # Traceback (most recent call last):
        #   Module zope.exceptions.tests.test_exceptionformatter, line ??, in testMultilineException
        #     exec \'syntax error\'
        #   File "<string>", line 1
        #     syntax error
        #            ^
        # SyntaxError: unexpected EOF while parsing
        self.assertEquals(s.splitlines()[-3:],
                          ['    syntax error',
                           '               ^',
                           'SyntaxError: unexpected EOF while parsing'])

    def testFormattedExceptionText(self):
        try:
            exec 'syntax error'
        except SyntaxError, se:
            s = tb(format="Hello, World! %(message)s")
        # Hello, World! Traceback (most recent call last):
        # Hello, World!   Module zope.exceptions.tests.test_exceptionformatter, line ??, in testFormattedExceptionText
        # Hello, World!     exec \'syntax error\'
        # Hello, World!   File "<string>", line 1
        # Hello, World!     syntax error
        # Hello, World!            ^
        # Hello, World! SyntaxError: unexpected EOF while parsing
        self.assertEquals(s.splitlines()[-3:],
                          ['Hello, World!     syntax error',
                           'Hello, World!                ^',
                           'Hello, World! SyntaxError: unexpected EOF while parsing'])

    def testFormattedExceptionHTML(self):
        try:
            exec 'syntax error'
        except SyntaxError, se:
            s = tb(as_html=1, format="Hello, World! %(message)s")
        # <p>Hello, World! Traceback (most recent call last):
        # <ul>
        # <li>Hello, World!   File "/Users/aaron/work/projects/zope.exceptions-traceback-log-formatting/src/zope/exceptions/tests/test_exceptionformatter.py", line 197, in testFormattedExceptionHTML<br />
        # Hello, World!     exec 'syntax error'</li>
        # </ul>Hello, World!   File "&lt;string&gt;", line 1<br />
        # Hello, World!     syntax error<br />
        # Hello, World!                ^<br />
        # Hello, World! SyntaxError: unexpected EOF while parsing<br />
        # </p>
        self.assertEquals(s.splitlines()[-4:],
                          ['Hello, World!     syntax error<br />',
                           'Hello, World!                ^<br />',
                           'Hello, World! SyntaxError: unexpected EOF while parsing<br />',
                           '</p>'])

def test_suite():
    return unittest.TestSuite([
        unittest.makeSuite(Test),
    ])

if __name__=='__main__':
    unittest.main(defaultTest='test_suite')
