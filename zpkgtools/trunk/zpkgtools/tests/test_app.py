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
"""Tests for zpkgtools.app."""

import os
import shutil
import sys
import unittest
import urllib

from StringIO import StringIO

from zpkgsetup import package
from zpkgsetup import publication
from zpkgsetup.tests import tempfileapi as tempfile

import zpkgtools

from zpkgtools import app
from zpkgtools import include
from zpkgtools import loader


CMD = "./foo/bar.py"


class CommandLineTestCase(unittest.TestCase):

    def parse_args(self, args):
        argv = [CMD] + args + ["resource"]
        options = app.parse_args(argv)
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

    def test_set_version_from_revision_tag(self):
        options = self.parse_args(["-r", "my-package-1_0"])
        self.assertEqual(options.version, "1.0")

    def test_set_package_revision_overrides_revision_tag(self):
        options = self.parse_args(["-r", "my-package-1_0", "-v1.0"])
        self.assertEqual(options.version, "1.0")

    def test_version_from_tagname(self):
        # Test only the version_from_tagname() function
        convert = app.version_from_tagname
        eq = self.assertEqual
        # Test with underscores (CVS style)
        eq(convert("my-package-1_0"), "1.0")
        eq(convert("my-package-1_0_42"), "1.0.42")
        eq(convert("my-package-1_0_42_24"), "1.0.42.24")
        eq(convert("my-package-1_0_42alpha42"), "1.0.42alpha42")
        eq(convert("my-package-1_0beta"), "1.0beta")
        eq(convert("my-package-1_0a666"), "1.0a666")
        eq(convert("my-package-1_0b777"), "1.0b777")
        eq(convert("my-package-1_0c888"), "1.0c888")
        # Test with underscores (Subversion style?)
        eq(convert("my-package-1.0"), "1.0")
        eq(convert("my-package-1.0.42"), "1.0.42")
        eq(convert("my-package-1.0.42.24"), "1.0.42.24")
        eq(convert("my-package-1.0.42alpha42"), "1.0.42alpha42")
        eq(convert("my-package-1.0beta"), "1.0beta")
        eq(convert("my-package-1.0a666"), "1.0a666")
        eq(convert("my-package-1.0b777"), "1.0b777")
        eq(convert("my-package-1.0c888"), "1.0c888")
        #
        # Check that unparsable tags return None
        #
        # Too many plain numeric segments
        eq(convert("my-package-1_0_42_24_39"), None)
        # Too many numeric segments after alphabetic segment
        eq(convert("my-package-1_0_42_alpha_24_35"), None)
        # Too few leading numeric seqments
        eq(convert("my-package-1"), None)
        eq(convert("my-package-1a"), None)
        eq(convert("my-package-1a0"), None)
        # Too many trailing numeric seqments
        eq(convert("mypkg-1_2_3alpha4_5"), None)

    def test_control_build_type(self):
        options = self.parse_args([])
        self.failIf(options.application)
        self.failIf(options.collect)
        # collection
        # short arg:
        options = self.parse_args(["-c"])
        self.failIf(options.application)
        self.failUnless(options.collect)
        # long arg:
        options = self.parse_args(["--collection"])
        self.failIf(options.application)
        self.failUnless(options.collect)
        # application
        # short arg:
        options = self.parse_args(["-a"])
        self.failUnless(options.application)
        self.failIf(options.collect)
        # long arg:
        options = self.parse_args(["--application"])
        self.failUnless(options.application)
        self.failIf(options.collect)
        # both
        # short args:
        options = self.parse_args(["-ac"])
        self.failUnless(options.application)
        self.failUnless(options.collect)
        options = self.parse_args(["-ca"])
        self.failUnless(options.application)
        self.failUnless(options.collect)
        options = self.parse_args(["-a", "-c"])
        self.failUnless(options.application)
        self.failUnless(options.collect)
        options = self.parse_args(["-c", "-a"])
        self.failUnless(options.application)
        self.failUnless(options.collect)
        # long args:
        options = self.parse_args(["--application", "--collection"])
        self.failUnless(options.application)
        self.failUnless(options.collect)
        options = self.parse_args(["--collection", "--application"])
        self.failUnless(options.application)
        self.failUnless(options.collect)


class ComponentTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="test-app-")
        self.mypkg_url = "file://" + urllib.pathname2url(self.tmpdir)
        self.ip = include.InclusionProcessor(loader.Loader())

    def write_app_file(self, name, text):
        f = open(os.path.join(self.tmpdir, name), "w")
        f.write(text)
        f.close()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_validation_of_package_without_setup_cfg(self):
        self.write_app_file("__init__.py", "# make this a package\n")
        #
        c = app.Component("mypkg", self.mypkg_url, self.ip)
        self.assert_(c.is_python_package())

    def test_validation_of_package_with_setup_cfg(self):
        self.write_app_file("SETUP.cfg", "# this is a simple package\n")
        self.write_app_file("__init__.py", "# make this a package\n")
        #
        c = app.Component("mypkg", self.mypkg_url, self.ip)
        self.assert_(c.is_python_package())

    def test_validation_of_nonpackage_with_setup_cfg(self):
        self.write_app_file("SETUP.cfg", "# this is a simple package\n")
        #
        c = app.Component("mypkg", self.mypkg_url, self.ip)
        self.assert_(not c.is_python_package())

    def test_non_validation_of_nonpackage_without_setup_cfg(self):
        self.assertRaises(zpkgtools.Error,
                          app.Component, "mypkg", self.mypkg_url, self.ip)

    def test_component_metadata_is_copied_by_default(self):
        self.write_app_file(publication.PUBLICATION_CONF,
                            "Metadata-Version: 1.1\n"
                            "Name: mypkg\n")
        self.write_app_file(include.PACKAGE_CONF,
                            "# nothing to specify\n")
        self.write_app_file(package.PACKAGE_CONF,
                            "# nothing to specify\n")
        #
        c = app.Component("mypkg", self.mypkg_url, self.ip)
        dest = tempfile.mkdtemp(prefix="test-app-dest-")
        try:
            c.write_package(dest)
            c.write_setup_cfg()
            c.write_setup_py(version='1.2.3')
            # done writing; make sure the expected metadata files are
            # present:
            pkgdest = os.path.join(dest, c.name)
            self.assert_(isfile(pkgdest, publication.PUBLICATION_CONF))
            self.assert_(isfile(pkgdest, package.PACKAGE_CONF))
            self.failIf(os.path.exists(os.path.join(pkgdest,
                                                    include.PACKAGE_CONF)))
        finally:
            shutil.rmtree(dest)

    def test_component_metadata_is_copied_with_inclusions(self):
        self.write_app_file(publication.PUBLICATION_CONF,
                            "Metadata-Version: 1.1\n"
                            "Name: mypkg\n")
        self.write_app_file(include.PACKAGE_CONF,
                            "<collection>\n"
                            "  README.txt README\n"
                            "</collection>\n")
        self.write_app_file(package.PACKAGE_CONF,
                            "# nothing to specify\n")
        self.write_app_file("README",
                            "some text\n")
        #
        c = app.Component("mypkg", self.mypkg_url, self.ip)
        dest = tempfile.mkdtemp(prefix="test-app-dest-")
        try:
            c.write_package(dest)
            c.write_setup_cfg()
            c.write_setup_py(version='1.2.3')
            # done writing; make sure the expected metadata files are
            # present:
            pkgdest = os.path.join(dest, c.name)
            self.assert_(isfile(pkgdest, publication.PUBLICATION_CONF))
            self.assert_(isfile(pkgdest, package.PACKAGE_CONF))
            self.assert_(isfile(pkgdest, "README.txt"))
            self.failIf(os.path.exists(os.path.join(pkgdest,
                                                    include.PACKAGE_CONF)))
        finally:
            shutil.rmtree(dest)


def isfile(path, *args):
    if args:
        path = os.path.join(path, *args)
    return os.path.isfile(path)


def test_suite():
    suite = unittest.makeSuite(CommandLineTestCase)
    suite.addTest(unittest.makeSuite(ComponentTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
