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
"""Tests of zope.importtool.app.

$Id$
"""
import os
import sys
import unittest

from StringIO import StringIO

from zope.importtool import app


class OptionsTestCase(unittest.TestCase):

    def test_basic_command_line(self):
        argv = ["foo/bar.py", "somescript", "arg1", "-opt", "arg2"]
        opts = app.Options(argv)
        self.assertEqual(opts.program, "bar.py")
        self.assertEqual(opts.script, "somescript")
        self.assertEqual(opts.argv, argv[1:])

    def test_just_script_name(self):
        argv = ["foo/bar.py", "somescript"]
        opts = app.Options(argv)
        self.assertEqual(opts.program, "bar.py")
        self.assertEqual(opts.script, "somescript")
        self.assertEqual(opts.argv, argv[1:])

    def test_missing_script_name(self):
        # This tests calls app.main() instead of app.Options() since
        # the main() function is responsible for generating the usage
        # message, and we want to check that there was a message on
        # stderr.
        old_stderr = sys.stderr
        sys.stderr = StringIO()
        try:
            try:
                app.main(["foo/bar.py"])
            finally:
                error_output = sys.stderr.getvalue()
                sys.stderr = old_stderr
        except SystemExit, e:
            self.failUnless(error_output)
            self.assertEqual(e.code, 2)
        else:
            self.fail("expected SystemExit")


class FirstImportReporterTestCase(unittest.TestCase):

    def setUp(self):
        self.old_stdout = sys.stdout
        self.old_stderr = sys.stderr
        sys.stdout = StringIO()
        sys.stderr = StringIO()

    def tearDown(self):
        sys.stdout = self.old_stdout
        sys.stderr = self.old_stderr

    def test_running_script(self):
        here = os.path.dirname(__file__)
        script = os.path.join(here, "script.py")
        app.main(["foo/bar.py", script, "splat", "-opt", "surge"])
        self.failIf(sys.stderr.getvalue())
        self.assertEqual(sys.stdout.getvalue(),
                         EXPECTED_OUTPUT)

EXPECTED_OUTPUT = """\
script ran
args: ['splat', '-opt', 'surge']
__name__ = __main__

------------
sys __main__
"""


def test_suite():
    suite = unittest.makeSuite(OptionsTestCase)
    suite.addTest(unittest.makeSuite(FirstImportReporterTestCase))
    return suite
