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
"""Tests for zpkgtools.app."""

import unittest

from zpkgtools import app


CMD = "./foo/bar.py"


class CommandLineTestCase(unittest.TestCase):

    def test_set_package_version(self):
        options, args = app.parse_args([CMD])
        self.assertEqual(options.version, "0.0.0")
        options, args = app.parse_args([CMD, "-v0.0.0"])
        self.assertEqual(options.version, "0.0.0")
        options, args = app.parse_args([CMD, "-v", "0.0.0"])
        self.assertEqual(options.version, "0.0.0")
        options, args = app.parse_args([CMD, "-v1.2"])
        self.assertEqual(options.version, "1.2")
        options, args = app.parse_args([CMD, "-v", "1.2"])
        self.assertEqual(options.version, "1.2")

    def test_suppress_support_code(self):
        options, args = app.parse_args([CMD])
        self.assert_(options.include_support_code is None)
        options, args = app.parse_args([CMD, "-s"])
        self.assert_(options.include_support_code)
        options, args = app.parse_args([CMD, "-S"])
        self.assert_(not options.include_support_code)

    def test_set_package_revision(self):
        options, args = app.parse_args([CMD])
        self.assertEqual(options.revision_tag, "HEAD")
        # short option:
        options, args = app.parse_args([CMD, "-rHEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options, args = app.parse_args([CMD, "-r", "HEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options, args = app.parse_args([CMD, "-rtag"])
        self.assertEqual(options.revision_tag, "tag")
        options, args = app.parse_args([CMD, "-r", "tag"])
        self.assertEqual(options.revision_tag, "tag")
        # long option, one arg:
        options, args = app.parse_args([CMD, "--revision-tag=HEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options, args = app.parse_args([CMD, "--revision-tag=tag"])
        self.assertEqual(options.revision_tag, "tag")
        # long option, two args:
        options, args = app.parse_args([CMD, "--revision-tag", "HEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options, args = app.parse_args([CMD, "--revision-tag", "tag"])
        self.assertEqual(options.revision_tag, "tag")

    def test_set_release_name(self):
        options, args = app.parse_args([CMD])
        self.assert_(options.release_name is None)
        # short option:
        options, args = app.parse_args([CMD, "-nFooPackage"])
        self.assertEqual(options.release_name, "FooPackage")
        options, args = app.parse_args([CMD, "-n", "FooPackage"])
        self.assertEqual(options.release_name, "FooPackage")
        # long option, one arg:
        options, args = app.parse_args([CMD, "--name=FooPackage"])
        self.assertEqual(options.release_name, "FooPackage")
        # long option, two args:
        options, args = app.parse_args([CMD, "--name", "FooPackage"])
        self.assertEqual(options.release_name, "FooPackage")

    def test_resource_map_list(self):
        options, args = app.parse_args([CMD])
        self.assertEqual(options.location_maps, [])
        # short option:
        options, args = app.parse_args([CMD, "-msomepath.map"])
        self.assertEqual(options.location_maps, ["somepath.map"])
        options, args = app.parse_args([CMD, "-msomepath.map",
                                        "-m", "another.map"])
        self.assertEqual(options.location_maps,
                         ["somepath.map", "another.map"])
        # long option:
        options, args = app.parse_args([CMD, "--resource-map=somepath.map"])
        self.assertEqual(options.location_maps, ["somepath.map"])
        options, args = app.parse_args([CMD,
                                        "--resource-map=somepath.map",
                                        "--resource-map", "another.map"])
        self.assertEqual(options.location_maps,
                         ["somepath.map", "another.map"])

    def test_suppress_config_file(self):
        # This is a little tricky; we use a magic value to indicate
        # that no config file should not be loaded.  If the value is
        # None, we should read the default config file it it exists,
        # but if the value is '', we shouldn't read one at all.  This
        # assumes the user isn't a complete fool (and doesn't pass ''
        # explicitly on the command line).
        #
        options, args = app.parse_args([CMD])
        self.assert_(options.configfile is None)
        options, args = app.parse_args([CMD, "-f"])
        self.assertEqual(options.configfile, "")

    def test_set_config_file(self):
        options, args = app.parse_args([CMD])
        self.assert_(options.configfile is None)
        # short option:
        options, args = app.parse_args([CMD, "-Csomepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")
        options, args = app.parse_args([CMD, "-C", "somepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")
        # long option:
        options, args = app.parse_args([CMD, "--configure=somepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")
        options, args = app.parse_args([CMD, "--configure", "somepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")


def test_suite():
    return unittest.makeSuite(CommandLineTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
