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

import zpkgsetup

from zpkgsetup import package
from zpkgsetup import publication
from zpkgsetup import urlutils
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

    def test_distribution_class(self):
        options = self.parse_args([])
        self.failIf(options.distribution_class)
        # long arg:
        options = self.parse_args(["--distribution", "pkg.mod.Cls"])
        self.assertEqual(options.distribution_class, "pkg.mod.Cls")
        options = self.parse_args(["--distribution=pkg.mod.Cls"])
        self.assertEqual(options.distribution_class, "pkg.mod.Cls")

    def test_support_packages(self):
        options = self.parse_args([])
        self.assertEqual(options.support_packages, [])
        # one package:
        options = self.parse_args(["--support", "pkg"])
        self.assertEqual(options.support_packages, ["pkg"])
        # two packages
        options = self.parse_args(["--support", "pkg1", "--support=pkg2"])
        self.assertEqual(options.support_packages, ["pkg1", "pkg2"])

    def test_exclude_resources(self):
        options = self.parse_args([])
        self.assertEqual(options.exclude_packages, [])
        # one package, short option:
        options = self.parse_args(["-x", "pkg"])
        self.assertEqual(options.exclude_packages, ["pkg"])
        # one package, long option:
        options = self.parse_args(["--exclude", "pkg"])
        self.assertEqual(options.exclude_packages, ["pkg"])
        # two packages:
        options = self.parse_args(["--exclude=pkg1", "-xpkg2"])
        self.assertEqual(options.exclude_packages, ["pkg1", "pkg2"])


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


class BuilderApplicationTestCase(unittest.TestCase):
    """Tests of the BuilderApplication object.

    These are pretty much functional tests since they start with a
    command line, though they don't run in an external process.

    """

    def setUp(self):
        self.app = None
        self.extra_files = []

    def tearDown(self):
        if self.app is not None:
            self.app.delayed_cleanup()
            self.app = None
        for fn in self.extra_files:
            os.unlink(fn)

    def createApplication(self, args):
        options = app.parse_args([CMD] + args)
        self.app = DelayedCleanupBuilderApplication(options)
        return self.app

    def createPackageMap(self):
        input = os.path.join(os.path.dirname(__file__), "input")
        input = os.path.abspath(input)
        package_map = os.path.join(input, "tmp-packages.map")
        shutil.copy(os.path.join(input, "packages.map"), package_map)
        self.extra_files.append(package_map)
        zpkgsetup_path = os.path.abspath(zpkgsetup.__path__[0])
        zpkgsetup_path = "file://" + urllib.pathname2url(zpkgsetup_path)
        f = open(package_map, "a")
        print >>f
        print >>f, "zpkgsetup", zpkgsetup_path
        f.close()
        # convert package_map to URL so relative names are resolved properly
        return "file://" + urllib.pathname2url(package_map)

    def test_adding_extra_support_code(self):
        package_map = self.createPackageMap()
        app = self.createApplication(
            ["-f", "-m", package_map, "--support", "package", "package"])
        app.run()
        # make sure the extra support code is actually present:
        support_dir = os.path.join(app.destination, "Support")
        package_dir = os.path.join(support_dir, "package")
        self.assert_(os.path.isdir(package_dir))
        self.assert_(isfile(package_dir, "__init__.py"))

    def test_alternate_distclass(self):
        # create the distribution tree:
        package_map = self.createPackageMap()
        app = self.createApplication(
            ["-f", "-m", package_map,
             "--distribution", "mysupport.MyDistribution", "package"])
        app.run()

        # Add the example distribution class to the built distro:
        mysupport = os.path.join(app.destination, "Support", "mysupport.py")
        f = open(mysupport, "w")
        print >>f, "import distutils.dist"
        print >>f, "class MyDistribution(distutils.dist.Distribution):"
        print >>f, "    this_is_mine = 42"
        f.close()

        # Run the setup.py from the distro and check that we got the
        # specialized distribution class.  This is really tricky since
        # we're running what's intended to be an script run in it's
        # own process inside our process, so we're trying to make
        # __main__ really look like it's running a script.  And then
        # we have to restore it.  There's something general lurking
        # here....
        import __builtin__
        import __main__
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        old_sys_argv = sys.argv[:]
        old_sys_path = sys.path[:]
        old_main_dict = __main__.__dict__.copy()
        old_cwd = os.getcwd()
        setup_script = os.path.join(app.destination, "setup.py")
        sio = StringIO()
        d = {"__file__": setup_script,
             "__name__": "__main__",
             "__doc__": None,
             "__builtins__": __builtin__.__dict__}
        try:
            sys.stdout = sys.stderr = sio
            sys.path.insert(0, os.path.join(app.destination, "Support"))
            sys.argv[:] = [setup_script, "-q", "-n", "--name"]
            import mysupport
            __main__.__dict__.clear()
            __main__.__dict__.update(d)
            os.chdir(app.destination)

            execfile(setup_script, __main__.__dict__)
            context = __main__.context

        finally:
            os.chdir(old_cwd)
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            sys.argv[:] = old_sys_argv
            sys.path[:] = old_sys_path
            __main__.__dict__.clear()
            __main__.__dict__.update(old_main_dict)

        # This makes sure that context.get_distribution_class()
        # returns the expected class; the actual instance of the class
        # that's used isn't available to us here, or we'd look at the
        # instance instead.
        #
        cls = context.get_distribution_class()
        self.assert_(cls is mysupport.MyDistribution)

    def test_relative_paths_in_cmdline_resource_maps(self):
        """Make sure that paths passed to the -m option become URLs.

        The resource maps and loader tools like to think of addresses
        as URLs, so paths passed in on the command line need to become
        URLs before being processed; this ensures that happens and
        that relative paths inside a resource map are handled
        correctly in that case (not just when referenced from a
        configuration file).

        """
        orig_pwd = os.getcwd()
        here = os.path.dirname(os.path.abspath(__file__))
        mapfile = os.path.join("input", "packages.map")
        args = ["-f", "-m", mapfile, "package"]
        os.chdir(here)
        try:
            app = self.createApplication(args)
            pkgurl = "file://%s/" % urlutils.pathname2url(
                os.path.join(here, "input", "package"))
            self.assertEqual(app.locations["package"], pkgurl)
        finally:
            os.chdir(orig_pwd)


class DelayedCleanupBuilderApplication(app.BuilderApplication):

    def create_tarball(self):
        pass

    def cleanup(self):
        pass

    def delayed_cleanup(self):
        app.BuilderApplication.cleanup(self)



def isfile(path, *args):
    if args:
        path = os.path.join(path, *args)
    return os.path.isfile(path)


def test_suite():
    suite = unittest.makeSuite(CommandLineTestCase)
    suite.addTest(unittest.makeSuite(ComponentTestCase))
    suite.addTest(unittest.makeSuite(BuilderApplicationTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
