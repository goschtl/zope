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

    def parse_args(self, args):
        args = [CMD] + args + ["resource"]
        options = app.parse_args(args)
        self.assertEqual(options.resource, "resource")
        return options

    def test_set_package_version(self):
        options = self.parse_args([])
        self.assertEqual(options.version, "0.0.0")
        options = self.parse_args(["-v0.0.0"])
        self.assertEqual(options.version, "0.0.0")
        options = self.parse_args(["-v", "0.0.0"])
        self.assertEqual(options.version, "0.0.0")
        options = self.parse_args(["-v1.2"])
        self.assertEqual(options.version, "1.2")
        options = self.parse_args(["-v", "1.2"])
        self.assertEqual(options.version, "1.2")

    def test_suppress_support_code(self):
        options = self.parse_args([])
        self.assert_(options.include_support_code is None)
        options = self.parse_args(["-s"])
        self.assert_(options.include_support_code)
        options = self.parse_args(["-S"])
        self.assert_(not options.include_support_code)

    def test_set_package_revision(self):
        options = self.parse_args([])
        self.assertEqual(options.revision_tag, "HEAD")
        # short option:
        options = self.parse_args(["-rHEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options = self.parse_args(["-r", "HEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options = self.parse_args(["-rtag"])
        self.assertEqual(options.revision_tag, "tag")
        options = self.parse_args(["-r", "tag"])
        self.assertEqual(options.revision_tag, "tag")
        # long option, one arg:
        options = self.parse_args(["--revision-tag=HEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options = self.parse_args(["--revision-tag=tag"])
        self.assertEqual(options.revision_tag, "tag")
        # long option, two args:
        options = self.parse_args(["--revision-tag", "HEAD"])
        self.assertEqual(options.revision_tag, "HEAD")
        options = self.parse_args(["--revision-tag", "tag"])
        self.assertEqual(options.revision_tag, "tag")

    def test_set_release_name(self):
        options = self.parse_args([])
        self.assert_(options.release_name is None)
        # short option:
        options = self.parse_args(["-nFooPackage"])
        self.assertEqual(options.release_name, "FooPackage")
        options = self.parse_args(["-n", "FooPackage"])
        self.assertEqual(options.release_name, "FooPackage")
        # long option, one arg:
        options = self.parse_args(["--name=FooPackage"])
        self.assertEqual(options.release_name, "FooPackage")
        # long option, two args:
        options = self.parse_args(["--name", "FooPackage"])
        self.assertEqual(options.release_name, "FooPackage")

    def test_resource_map_list(self):
        options = self.parse_args([])
        self.assertEqual(options.location_maps, [])
        # short option:
        options = self.parse_args(["-msomepath.map"])
        self.assertEqual(options.location_maps, ["somepath.map"])
        options = self.parse_args(["-msomepath.map",
                                   "-m", "another.map"])
        self.assertEqual(options.location_maps,
                         ["somepath.map", "another.map"])
        # long option:
        options = self.parse_args(["--resource-map=somepath.map"])
        self.assertEqual(options.location_maps, ["somepath.map"])
        options = self.parse_args(["--resource-map=somepath.map",
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
        options = self.parse_args([])
        self.assert_(options.configfile is None)
        options = self.parse_args(["-f"])
        self.assertEqual(options.configfile, "")

    def test_set_config_file(self):
        options = self.parse_args([])
        self.assert_(options.configfile is None)
        # short option:
        options = self.parse_args(["-Csomepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")
        options = self.parse_args(["-C", "somepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")
        # long option:
        options = self.parse_args(["--configure=somepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")
        options = self.parse_args(["--configure", "somepath.conf"])
        self.assertEqual(options.configfile, "somepath.conf")


def test_suite():
    return unittest.makeSuite(CommandLineTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
