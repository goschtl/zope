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
"""Tests for the inclusion processor."""

import filecmp
import os
import shutil
import tempfile
import unittest
import urllib2

from os.path import join
from StringIO import StringIO

from zpkgtools import cvsloader
from zpkgtools import include


class InclusionProcessorTestCase(unittest.TestCase):

    def setUp(self):
        self.source = os.path.dirname(__file__)
        self.destination = tempfile.mkdtemp(prefix="test_include_")
        self.processor = include.InclusionProcessor(self.source,
                                                    self.destination)
        self.source = os.path.abspath(self.source)

    def tearDown(self):
        shutil.rmtree(self.destination)

    def test_simple_includespec(self):
        f = StringIO("""
          # This is a comment.  It should be ignored.

          foo.html         http://www.python.org/index.html
          doc/whatzit.txt  repository:doc/whatzit.txt
          ignorethis.txt   -

          # Another comment.
          """)
        spec = include.Specification(self.source)
        spec.load(f, "<string>")
        self.assertEqual(len(spec.excludes), 1)
        self.assertEqual(len(spec.includes), 2)
        self.assert_(join(self.source, "ignorethis.txt")
                     in spec.excludes)
        self.assertEqual(spec.includes["foo.html"],
                         "http://www.python.org/index.html")
        self.assertEqual(spec.includes[join("doc", "whatzit.txt")],
                         "repository:doc/whatzit.txt")

    def test_error_on_nonexistant_ignore(self):
        f = StringIO("""
            does-not-exist.txt  -
            """)
        spec = include.Specification(self.source)
        try:
            spec.load(f, "<string>")
        except include.InclusionSpecificationError, e:
            self.assertEqual(e.filename, "<string>")
            self.assertEqual(e.lineno, 2)
        else:
            self.fail("expected InclusionSpecificationError")

    def test_error_on_omitted_source(self):
        f = StringIO("whatzit.txt \n")
        spec = include.Specification(self.source)
        try:
            spec.load(f, "<string>")
        except include.InclusionSpecificationError, e:
            self.assertEqual(e.filename, "<string>")
            self.assertEqual(e.lineno, 1)
        else:
            self.fail("expected InclusionSpecificationError")

    def test_globbing_on_ignore(self):
        f = StringIO("*.txt -")
        spec = include.Specification(self.source)
        spec.load(f, "<string>")
        self.assertEqual(len(spec.excludes), 1)
        self.assert_(join(self.source, "ignorethis.txt")
                     in spec.excludes)

    def test_normalizePath(self):
        normalize = include.Specification("foo").normalizePath
        self.check_normalize_paths(normalize)

    def test_normalizePathOrURL(self):
        normalize = include.Specification("foo").normalizePathOrURL
        self.check_normalize_paths(normalize)
        self.check_normalize_urls(normalize)

    def check_normalize_paths(self, normalize):
        INCLUDES = "INCLUDES.txt"
        self.assertEqual(normalize("README.txt", "t", INCLUDES, 1),
                         "README.txt")
        self.assertEqual(normalize("doc/README.txt", "t", INCLUDES, 2),
                         join("doc", "README.txt"))
        # Ignore this because it looks like a Windows drive letter:
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "c:foo/bar", "t", INCLUDES, 3)
        # Absolute paths are an error as well:
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "/absolute/path", "t", INCLUDES, 4)
        # Relative paths that point up the hierarchy are also disallowed:
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "abc/../../def.txt", "t", INCLUDES, 5)
        self.assertRaises(include.InclusionSpecificationError,
                          normalize, "../def.txt", "t", INCLUDES, 6)

    def check_normalize_urls(self, normalize):
        INCLUDES = "INCLUDES.txt"
        for url in ("http://www.example.com/index.html",
                    "repository:/Zope3/doc",
                    "cvs://cvs.zope.com/cvs-repository:/Zope3/doc:HEAD"):
            self.assertEqual(normalize(url, "t", INCLUDES, 1), url)

    def test_createDistributionTree_creates_destination(self):
        os.rmdir(self.destination)
        self.processor.createDistributionTree()
        self.assert_(os.path.isdir(self.destination))
        self.assert_(os.path.isfile(join(self.destination, "ignorethis.txt")))

    def test_createDistributionTree(self):
        spec = include.Specification(self.source)
        spec.load(StringIO("__init__.py -"), "<string>")
        self.processor.createDistributionTree(spec)
        self.check_file("ignorethis.txt")
        self.check_file("somescript.py")
        self.assert_(not os.path.exists(join(self.destination, "__init__.py")))
        self.assert_(not os.path.exists(join(self.destination, "CVS")))
        self.assert_(not os.path.exists(join(self.destination, ".cvsignore")))

    def check_file(self, name):
        srcname = join(self.source, name)
        destname = join(self.destination, name)
        self.assert_(os.path.isfile(destname))
        srcstat = os.stat(srcname)
        deststat = os.stat(destname)
        self.assertEqual(srcstat.st_mode, deststat.st_mode)
        self.assertEqual(srcstat.st_mtime, deststat.st_mtime)
        self.assertEqual(srcstat.st_atime, deststat.st_atime)

    def test_including_from_cvs_url(self):
        self.start_including_from_cvs_url()
        self.processor.addSingleInclude(
            "somedir",
            "cvs://cvs.zope.org:pserver/cvs-repository:Zope3")
        cvsurl, destination = self.args
        self.assertEqual(cvsurl.getUrl(),
                         "cvs://cvs.zope.org:pserver/cvs-repository:Zope3")
        self.assertEqual(destination,
                         os.path.join(self.destination, "somedir"))

    def test_including_from_cvs_url_without_base(self):
        self.start_including_from_cvs_url()
        self.processor.cvsurl = None
        self.processor.addSingleInclude(
            "somedir",
            "cvs://cvs.zope.org:pserver/cvs-repository:Zope3")
        cvsurl, destination = self.args
        self.assertEqual(cvsurl.getUrl(),
                         "cvs://cvs.zope.org:pserver/cvs-repository:Zope3")
        self.assertEqual(destination,
                         os.path.join(self.destination, "somedir"))

    def test_including_from_repository_url(self):
        self.start_including_from_cvs_url()
        self.processor.addSingleInclude("somedir", "repository:somedir:TAG")
        cvsurl, destination = self.args
        self.assertEqual(
            cvsurl.getUrl(),
            "cvs://cvs.example.org:ext/foo:module/dir/somedir:TAG")
        self.assertEqual(destination,
                         os.path.join(self.destination, "somedir"))

    def start_including_from_cvs_url(self):
        self.processor.cvsurl = cvsloader.parse(
            "cvs://cvs.example.org:ext/foo:module/dir/:TAG")
        self.processor.includeFromUrl = lambda src, dst: self.fail(
            "not expected to load via URL")
        self.processor.includeFromLocalTree = lambda src, dst: self.fail(
            "not expected to load from local tree")
        self.processor.includeFromCvs = self.save_args

    def save_args(self, *args):
        self.args = args

    def test_including_from_repository_url_without_base(self):
        # When using a repository: URL, there must be a base cvs: URL
        # for the InclusionProcessor.
        self.processor.cvsurl = None
        self.assertRaises(include.InclusionError,
                          self.processor.addSingleInclude,
                          "somedir", "repository:somedir:TAG")

    def test_including_from_url(self):
        URL = "http://www.example.org/"
        old_urlopen = urllib2.urlopen
        self.called = False
        def my_urlopen(url):
            self.assertEqual(url, URL)
            self.called = True
            return StringIO("my_urlopen_data\n")
        urllib2.urlopen = my_urlopen
        try:
            self.processor.addSingleInclude("somefile.txt", URL)
        finally:
            urllib2.urlopen = old_urlopen
        self.assert_(self.called)
        resultfile = os.path.join(self.destination, "somefile.txt")
        self.assert_(os.path.isfile(resultfile))
        f = open(resultfile, "rU")
        text = f.read()
        f.close()
        self.assertEqual(text, "my_urlopen_data\n")

    def test_including_from_file(self):
        # This also tests the automatic creation of a required output
        # directory.
        FILENAME = "ignorethis.txt"
        self.processor.includeFromCvs = lambda src, dst: self.fail(
            "not expected to load from CVS")
        self.processor.includeFromUrl = lambda src, dst: self.fail(
            "not expected to load via URL")
        self.processor.addSingleInclude("foo/splat.txt", FILENAME)
        sourcefile = os.path.join(self.source, FILENAME)
        resultfile = os.path.join(self.destination, "foo", "splat.txt")
        self.assert_(os.path.isfile(resultfile))
        self.assert_(filecmp.cmp(resultfile, sourcefile, shallow=False))


def test_suite():
    return unittest.makeSuite(InclusionProcessorTestCase)

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
