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
"""Tests for zope.importtool.hook.

$Id$
"""
import __builtin__
import sys
import unittest

from zope.importtool import hook
from zope.importtool import reporter
from zope.importtool.tests import sample


real__import__ = __import__


def alternate_hook(*args):
    return real__import__(*args)


class TestException(Exception):
    """Exception raised in the tests."""


class ReporterRaiseOnFound(reporter.Reporter):

    def found(self, *args):
        raise TestException("found")


class ReporterRaiseOnRequest(reporter.Reporter):

    def request(self, *args):
        raise TestException("request")


class HookTestCase(unittest.TestCase):

    def setUp(self):
        self.reports = []

    def tearDown(self):
        hook.reset()

    def request(self, importer, name, fromlist):
        self.reports.append(name)

    def found(self, importer, imported, fromlist):
        name = self.reports.pop()
        self.reports.append((importer, imported, name, fromlist))

    def raise_error(self, *args):
        self.reports.append(args)
        raise TestException()

    def test_normal_installation(self):
        self.failIf(hook.active())
        hook.install_reporter(self)
        self.failIf(not hook.active())
        hook.uninstall_reporter()
        self.failIf(hook.active())
        # now do it again, to make sure we really can re-install the hook
        hook.install_reporter(self)
        self.failIf(not hook.active())

    def test_reinstall_fails_if_active(self):
        hook.install_reporter(self)
        self.assertRaises(RuntimeError, hook.install_reporter, self)

    def test_uninstall_fails_if_never_active(self):
        self.assertRaises(RuntimeError, hook.uninstall_reporter)

    def test_uninstall_fails_if_no_longer_active(self):
        hook.install_reporter(self)
        hook.uninstall_reporter()
        self.assertRaises(RuntimeError, hook.uninstall_reporter)

    def test_wrap_other_hook(self):
        __builtin__.__import__ = alternate_hook
        hook.install_reporter(self)
        self.failUnless(hook.active())
        hook.uninstall_reporter()
        self.failIf(hook.active())
        self.failUnless(__builtin__.__import__ is alternate_hook)

    def test_report_record(self):
        hook.install_reporter(self)
        import sys
        import sys
        from sample import THE_ANSWER
        self.assertEqual(
            self.reports,
            [(__name__, "sys", "sys", None),
             (__name__, "sys", "sys", None),
             (__name__, "zope.importtool.tests.sample", "sample",
              ("THE_ANSWER",)),
             ])

    def test_exception_on_request(self):
        hook.install_reporter(ReporterRaiseOnRequest())
        try:
            import sys
        except TestException, e:
            self.assertEqual(e[0], "request")
        else:
            self.fail("expected TestException")

    def test_exception_on_found(self):
        hook.install_reporter(ReporterRaiseOnFound())
        try:
            import sys
        except TestException, e:
            self.assertEqual(e[0], "found")
        else:
            self.fail("expected TestException")

    def test_direct_calls(self):
        # make sure the hook function can be called directly as well,
        # and behave the way the default __import__() works
        hook.install_reporter(self)
        m = __import__("sys")
        self.assertEqual(self.reports[-1],
                         (__name__, "sys", "sys", None))
        self.failUnless(m is sys)
        m = __import__("sample")
        self.assertEqual(self.reports[-1],
                         (__name__, "zope.importtool.tests.sample", "sample",
                          None))
        self.failUnless(m is sample)
        m = __import__("sys", {"__name__": "foo.bar"})
        self.assertEqual(self.reports[-1],
                         ("foo.bar", "sys", "sys", None))
        self.failUnless(m is sys)
        __import__("sys", {"__name__": "foo.bar"}, {}, ("splat", "splurt"))
        self.assertEqual(self.reports[-1],
                         ("foo.bar", "sys", "sys", ("splat", "splurt")))
        m = __import__("zope.importtool.tests.sample", globals(), {},
                       ("THE_ANSWER",))
        self.failUnless(m is sample)


def test_suite():
    return unittest.makeSuite(HookTestCase)
