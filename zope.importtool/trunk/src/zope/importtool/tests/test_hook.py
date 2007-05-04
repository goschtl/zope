##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Tests for zope.importtool.hook.

$Id$
"""
import __builtin__
import sys
import unittest

from zope.importtool import hook
from zope.importtool import reporter
from zope.importtool.tests import sample


THIS_PACKAGE = __name__[:__name__.rfind(".")]
PARENT_PACKAGE = THIS_PACKAGE[:THIS_PACKAGE.rfind(".")]

real__import__ = __import__


def alternate_hook(*args):
    return real__import__(*args)


class TestException(Exception):
    """Exception raised in the tests."""


class ReporterRaiseOnFound(reporter.Reporter):

    def found(self, *args):
        raise TestException("found")


class ReporterRaiseOnException(reporter.Reporter):

    def exception(self, *args):
        raise TestException("exception")


class ReporterRaiseOnRequest(reporter.Reporter):

    def request(self, *args):
        raise TestException("request")


class HookTestCase(unittest.TestCase):

    def setUp(self):
        self.reports = []
        self.__import__ = __import__

    def tearDown(self):
        __builtin__.__import__ = self.__import__

    def get_hook(self, reporter=None):
        if reporter is None:
            reporter = self
        return hook.ReportingHook(reporter)

    # reporter methods

    def request(self, importer, name, fromlist):
        self.reports.append(("<request>", importer, name))

    def found(self, importer, imported, fromlist):
        self.reports.append(("<found>", importer, imported, fromlist))

    def exception(self, importer, name, fromlist, exc_info):
        self.reports.append(("<exception>", importer, name, fromlist))
        self.exc_info = exc_info

    # test methods

    def test_normal_installation(self):
        h = self.get_hook()
        self.failIf(h.active)
        h.install()
        self.failIf(not h.active)
        h.uninstall()
        self.failIf(h.active)
        # now do it again, to make sure we really can re-install the hook
        h.install()
        self.failIf(not h.active)

    def test_reinstall_fails_if_active(self):
        h = self.get_hook()
        h.install()
        self.assertRaises(RuntimeError, h.install)

    def test_uninstall_fails_if_never_active(self):
        h = self.get_hook()
        self.assertRaises(RuntimeError, h.uninstall)

    def test_uninstall_fails_if_no_longer_active(self):
        h = self.get_hook()
        h.install()
        h.uninstall()
        self.assertRaises(RuntimeError, h.uninstall)

    def test_wrap_other_hook(self):
        h = self.get_hook()
        __builtin__.__import__ = alternate_hook
        h.install()
        self.failUnless(h.active)
        h.uninstall()
        self.failIf(h.active)
        self.failUnless(__builtin__.__import__ is alternate_hook)

    def test_report_record(self):
        h = self.get_hook()
        h.install()
        import sys
        import sys
        from sample import THE_ANSWER
        expected = [
            ("<request>", __name__, "sys"),
            ("<found>",   __name__, "sys", None),
            ("<request>", __name__, "sys"),
            ("<found>",   __name__, "sys", None),
            ("<request>", __name__, "sample"),
            ("<found>",   __name__, "zope.importtool.tests.sample",
             ("THE_ANSWER",)),
            ]
        self.assertEqual(self.reports, expected)

    def test_exception_on_request(self):
        h = self.get_hook(ReporterRaiseOnRequest())
        h.install()
        try:
            import sys
        except TestException, e:
            self.assertEqual(e[0], "request")
        else:
            self.fail("expected TestException")

    def test_exception_on_found(self):
        h = self.get_hook(ReporterRaiseOnFound())
        h.install()
        try:
            import sys
        except TestException, e:
            self.assertEqual(e[0], "found")
        else:
            self.fail("expected TestException")

    def test_exception_on_exception(self):
        h = self.get_hook(ReporterRaiseOnException())
        h.install()
        try:
            import zope.importtools.tests.does_not_exist
        except TestException, e:
            self.assertEqual(e[0], "exception")
        else:
            self.fail("expected TestException")

    def test_direct_calls(self):
        # make sure the hook function can be called directly as well,
        # and behave the way the default __import__() works
        h = self.get_hook()
        h.install()
        m = __import__("sys")
        self.assertEqual(self.reports[-1],
                         ("<found>", __name__, "sys", None))
        self.failUnless(m is sys)
        m = __import__("sample")
        self.assertEqual(self.reports[-1],
                         ("<found>", __name__, "zope.importtool.tests.sample",
                          None))
        self.failUnless(m is sample)
        m = __import__("sys", {"__name__": "foo.bar"})
        self.assertEqual(self.reports[-1],
                         ("<found>", "foo.bar", "sys", None))
        self.failUnless(m is sys)
        __import__("sys", {"__name__": "foo.bar"}, {}, ("splat", "splurt"))
        self.assertEqual(self.reports[-1],
                         ("<found>", "foo.bar", "sys", ("splat", "splurt")))
        m = __import__("zope.importtool.tests.sample", globals(), {},
                       ("THE_ANSWER",))
        self.failUnless(m is sample)

    def test_reporting_exception_during_import(self):
        h = self.get_hook()
        h.install()
        try:
            import error
        except TestException, e:
            self.failUnless(e is self.exc_info[1])
            self.assertEqual(self.reports[-1],
                             ("<exception>", __name__, "error", None))
        else:
            self.fail("expected TestException")
        self.exc_info = None


class HelpFunctionTestCase(unittest.TestCase):

    def test_get_package_name(self):
        self.assertEqual(hook.get_package_name(globals()),
                         THIS_PACKAGE)
        self.assertEqual(hook.get_package_name(sys.__dict__), None)
        self.assertEqual(hook.get_package_name(reporter.__dict__),
                         PARENT_PACKAGE)
        import logging
        self.assertEqual(hook.get_package_name(logging.__dict__), "logging")


def test_suite():
    suite = unittest.makeSuite(HookTestCase)
    suite.addTest(unittest.makeSuite(HelpFunctionTestCase))
    return suite
