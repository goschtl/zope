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
import unittest

from zope.importtool import hook


real__import__ = __import__


def alternate_hook(*args):
    return real__import__(*args)


class TestException(Exception):
    """Exception raised in the tests."""


class HookTestCase(unittest.TestCase):

    def setUp(self):
        self.reports = []

    def tearDown(self):
        hook.reset()

    def report(self, *args):
        self.reports.append(args)

    def raise_error(self, *args):
        self.reports.append(args)
        raise TestException()

    def test_normal_installation(self):
        self.failIf(hook.active())
        hook.install_reporter(self.report)
        self.failIf(not hook.active())
        hook.uninstall_reporter()
        self.failIf(hook.active())
        # now do it again, to make sure we really can re-install the hook
        hook.install_reporter(self.report)
        self.failIf(not hook.active())

    def test_reinstall_fails_if_active(self):
        hook.install_reporter(self.report)
        self.assertRaises(RuntimeError, hook.install_reporter, self.report)

    def test_uninstall_fails_if_never_active(self):
        self.assertRaises(RuntimeError, hook.uninstall_reporter)

    def test_uninstall_fails_if_no_longer_active(self):
        hook.install_reporter(self.report)
        hook.uninstall_reporter()
        self.assertRaises(RuntimeError, hook.uninstall_reporter)

    def test_wrap_other_hook(self):
        __builtin__.__import__ = alternate_hook
        hook.install_reporter(self.report)
        self.failUnless(hook.active())
        hook.uninstall_reporter()
        self.failIf(hook.active())
        self.failUnless(__builtin__.__import__ is alternate_hook)

    def test_report_record(self):
        hook.install_reporter(self.report)
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

    def test_exception_from_reporter(self):
        hook.install_reporter(self.raise_error)
        try:
            import sys
        except TestException:
            self.assertEqual(len(self.reports), 1)
        else:
            self.fail("expected TestException")


def test_suite():
    return unittest.makeSuite(HookTestCase)
