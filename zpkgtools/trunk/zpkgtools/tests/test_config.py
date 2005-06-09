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
"""Tests for zpkgtools.config."""

import os
import shutil
import tempfile
import unittest

from StringIO import StringIO

from zpkgsetup import cfgparser
from zpkgsetup import urlutils
from zpkgtools import config


here = os.path.dirname(os.path.abspath(__file__))


class ConfigTestCase(unittest.TestCase):

    def test_defaultConfigurationPath(self):
        # Not really sure what makes sense to check here, but at least
        # make sure it returns a string:
        path = config.defaultConfigurationPath()
        self.assert_(isinstance(path, basestring))

    def test_constructor(self):
        cf = config.Configuration()
        self.assert_(cf.include_support_code)
        self.assertEqual(len(cf.locations), 0)
        self.assertEqual(len(cf.location_maps), 0)

    def test_loadPath(self):
        path = os.path.join(here, "zpkg-ok.conf")
        cf = config.Configuration()
        cf.loadPath(path)
        self.assertEqual(
            cf.location_maps,
            ["cvs://cvs.example.org/cvsroot:module/package/PACKAGES.txt",
             urlutils.file_url(os.path.join(here, "relative/path.txt"))])

    def test_constructor_bad_config_setting(self):
        # unknown option:
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, "unknown-option 42\n")

        # repository-map without path
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, "resource-map \n")

        # include-support-code too many times
        self.assertRaises(cfgparser.ConfigurationError,
                          self.load_text, ("include-support-code false\n"
                                           "include-support-code false\n"))

    def test_loadPath_no_such_file(self):
        path = os.path.join(here, "no-such-file")
        cf = config.Configuration()
        self.assertRaises(IOError, cf.loadPath, path)

    def load_text(self, text, path=None, basedir=None):
        if path is None:
            if basedir is None:
                basedir = "foo"
            path = os.path.join(basedir, "bar.conf")
        if basedir is None:
            os.path.dirname(path)
        cf = config.Configuration()
        sio = StringIO(text)
        cf.loadStream(sio, path, basedir)
        return cf


class ConfigurationLocationMapIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_relative_paths_mapped(self):
        os.mkdir(os.path.join(self.tmpdir, "releases"))
        reldir = os.path.join(self.tmpdir, "releases", "Thing")
        os.mkdir(reldir)
        cfgpath = os.path.join(reldir, "zpkg.conf")
        f = open(cfgpath, "w")
        f.write("resource-map one.map\n")
                #"resource-map two.map\n")
        f.close()
        mapfile = os.path.join(reldir, "one.map")
        f = open(mapfile, "w")
        f.write("pkg1 ../../src/pkg1\n"
                "pkg2 ../Thong\n"
                "pkg3 some/dir\n")
        f.close()

        cf = config.Configuration()
        old_path = os.getcwd()
        os.chdir(self.tmpdir)
        try:
            cf.loadPath("releases/Thing/zpkg.conf")
        finally:
            os.chdir(old_path)

        # make sure we're looking at the right location map:
        self.assertEqual(cf.location_maps, [urlutils.file_url(mapfile)])

        # load the finished map and make sure we get the right values:
        cf.finalize()
        expected = urlutils.file_url(
            os.path.join(self.tmpdir, "src", "pkg1"))
        self.assertEqual(cf.locations["pkg1"], expected)

        expected = urlutils.file_url(
            os.path.join(self.tmpdir, "releases", "Thong"))
        self.assertEqual(cf.locations["pkg2"], expected)

        expected = urlutils.file_url(
            os.path.join(self.tmpdir, "releases", "Thing", "some", "dir"))
        self.assertEqual(cf.locations["pkg3"], expected)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        unittest.makeSuite(ConfigTestCase))
    suite.addTest(
        unittest.makeSuite(ConfigurationLocationMapIntegrationTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
