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
"""Tests for zpkgtools.package."""

import doctest
import os.path
import shutil
import tempfile
import unittest

from distutils.core import Extension
from StringIO import StringIO

from zpkgtools import cfgparser
from zpkgtools import package


class PackageInfoTestCase(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp(prefix="test_package_")

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def write_config(self, text):
        f = open(os.path.join(self.tmpdir, package.PACKAGE_CONF), "w")
        f.write(text)
        f.close()

    def test_empty_pkginfo(self):
        self.write_config("# empty configuration file\n")
        pkginfo = package.loadPackageInfo("foo", self.tmpdir, "bar")
        eq = self.assertEqual
        eq(pkginfo.extensions, [])
        eq(pkginfo.documentation, [])
        eq(pkginfo.script, [])

    def test_missing_pkginfo(self):
        pkginfo = package.loadPackageInfo("foo", self.tmpdir, "bar")
        eq = self.assertEqual
        eq(pkginfo.extensions, [])
        eq(pkginfo.documentation, [])
        eq(pkginfo.script, [])

    def test_nonempty_pkginfo(self):
        self.write_config("documentation  doc/README.txt\n"
                          "script         bin/runme.py\n"
                          "<extension cricket>\n"
                          "  source     jiminy.c\n"
                          "  define     FOO\n"
                          "  define     BAR = splat\n"
                          "  undefine   CRUNCHY NUGGET\n"
                          "  depends-on cricket.h\n"
                          "  depends-on innerds.c\n"
                          "  language   C\n"
                          "</extension>\n")
        pkginfo = package.loadPackageInfo("foo", self.tmpdir, "bar")
        eq = self.assertEqual
        eq(len(pkginfo.extensions), 1)
        eq(pkginfo.documentation, ["bar/doc/README.txt"])
        eq(pkginfo.script, ["bar/bin/runme.py"])

        ext = pkginfo.extensions[0]
        self.assert_(isinstance(ext, Extension))
        eq(ext.name, "foo.cricket")
        eq(ext.sources, ["bar/jiminy.c"])
        eq(ext.depends, ["bar/cricket.h", "bar/innerds.c"])
        eq(ext.define_macros, [("FOO", None), ("BAR", "splat")])
        eq(ext.undef_macros, ["CRUNCHY", "NUGGET"])
        eq(ext.language, "C")

    def test_broken_extension_too_many_languages(self):
        self.write_config("<extension cricket>\n"
                          "  source     jiminy.c\n"
                          "  language   C\n"
                          "  language   C++\n"
                          "</extension>\n")
        self.assertRaises(cfgparser.ConfigurationError,
                          package.loadPackageInfo, "foo", self.tmpdir, "bar")

    def test_broken_extension_without_name(self):
        self.write_config("<extension>\n"
                          "  source  jiminy.c\n"
                          "</extension>\n")
        self.assertRaises(cfgparser.ConfigurationError,
                          package.loadPackageInfo, "foo", self.tmpdir, "bar")

    def test_broken_extension_no_source(self):
        self.write_config("<extension cricket/>")
        self.assertRaises(cfgparser.ConfigurationError,
                          package.loadPackageInfo, "foo", self.tmpdir, "bar")


def test_suite():
    suite = doctest.DocTestSuite("zpkgtools.package")
    suite.addTest(unittest.makeSuite(PackageInfoTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
