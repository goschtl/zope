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
"""Tests for zpkgtools.dependencies."""

import unittest

from StringIO import StringIO

from zpkgtools import dependencies


class DependenciesTestCase(unittest.TestCase):

    def test_empty_file(self):
        sio = StringIO("")
        deps = dependencies.load(sio)
        self.assert_(not deps.modules)
        self.assert_(not deps.others)

    def test_empty_file_with_comments(self):
        sio = StringIO("""\
            # This is a comment.
            # So is this.
            """)
        deps = dependencies.load(sio)
        self.assert_(not deps.modules)
        self.assert_(not deps.others)

    def test_just_modules(self):
        sio = StringIO("""\
            zope.foo
            zope.app.bar
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps.modules), 2)
        self.assert_("zope.foo" in deps.modules)
        self.assert_("zope.app.bar" in deps.modules)
        self.assert_(not deps.others)

    def test_just_others(self):
        sio = StringIO("""\
            not-a-module
            feature:zope.bar
            """)
        deps = dependencies.load(sio)
        self.assert_(not deps.modules)
        self.assertEqual(len(deps.others), 2)
        self.assert_("not-a-module" in deps.others)
        self.assert_("feature:zope.bar" in deps.others)

    def test_modules_and_others(self):
        sio = StringIO("""\
            not-a-module
            zope.foo
            # Comments can go here
            zope.app.bar
            feature:zope.bar
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps.modules), 2)
        self.assert_("zope.foo" in deps.modules)
        self.assert_("zope.app.bar" in deps.modules)
        self.assertEqual(len(deps.others), 2)
        self.assert_("not-a-module" in deps.others)
        self.assert_("feature:zope.bar" in deps.others)

    def test_blank_line_ends_data(self):
        sio = StringIO("""\
            zope.app
            zope.schema
            feature:foo

            feature:but-not-really
            zope.yeahright
            """)
        deps = dependencies.load(sio)
        self.assertEqual(len(deps.modules), 2)
        self.assertEqual(len(deps.others), 1)
        self.assert_("feature:but-not-really" not in deps.modules)
        self.assert_("feature:but-not-really" not in deps.others)
        self.assert_("zope.yeahright" not in deps.modules)
        self.assert_("zope.yeahright" not in deps.others)


def test_suite():
    return unittest.makeSuite(DependenciesTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
