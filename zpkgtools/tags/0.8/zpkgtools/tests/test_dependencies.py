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
"""Tests for zpkgtools.dependencies."""

import unittest

from StringIO import StringIO

from zpkgtools import dependencies


class DependenciesTestCase(unittest.TestCase):

    def test_empty_file(self):
        sio = StringIO("")
        deps = dependencies.load(sio)
        self.assert_(not deps)

    def test_empty_file_with_comments(self):
        sio = StringIO("""\
            # This is a comment.
            # So is this.
            """)
        deps = dependencies.load(sio)
        self.assert_(not deps)

    def test_just_packages(self):
        sio = StringIO("""\
            zope.foo
            zope.app.bar
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps), 2)
        self.assert_("zope.foo" in deps)
        self.assert_("zope.app.bar" in deps)

    def test_just_others(self):
        sio = StringIO("""\
            feature:not-a-module
            feature:zope.bar
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps), 2)
        self.assert_("feature:not-a-module" in deps)
        self.assert_("feature:zope.bar" in deps)

    def test_packages_and_others(self):
        sio = StringIO("""\
            feature:not-a-module
            zope.foo
            # Comments can go here
            zope.app.bar
            feature:zope.bar
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps), 4)
        self.assert_("zope.foo" in deps)
        self.assert_("zope.app.bar" in deps)
        self.assert_("feature:not-a-module" in deps)
        self.assert_("feature:zope.bar" in deps)

    def test_blank_line_is_ignored(self):
        sio = StringIO("""\
            zope.app
            zope.schema
            feature:foo

            feature:yes-really
            zope.yes_again
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps), 5)
        self.assert_("feature:foo" in deps)
        self.assert_("zope.app" in deps)
        self.assert_("zope.schema" in deps)
        self.assert_("feature:yes-really" in deps)
        self.assert_("zope.yes_again" in deps)


def test_suite():
    return unittest.makeSuite(DependenciesTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
