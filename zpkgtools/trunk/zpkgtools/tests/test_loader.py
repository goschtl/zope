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
"""Tests for the zpkgtools.loader module."""

import filecmp
import os
import shutil
import tempfile
import unittest
import urllib

from zpkgtools import loader
from zpkgtools.tests import test_svnloader


class LoaderTestBase(unittest.TestCase):

    def setUp(self):
        super(LoaderTestBase, self).setUp()
        self.workingdir = tempfile.mkdtemp(prefix="test-workdir-")
        self.cvsdir = os.path.join(self.workingdir, "CVS")
        os.mkdir(self.cvsdir)

    def tearDown(self):
        super(LoaderTestBase, self).tearDown()
        shutil.rmtree(self.workingdir)

    def createLoader(self, tag=None):
        return loader.Loader(tag)


class LoaderTestCase(LoaderTestBase, test_svnloader.SubversionRepositoryBase):

    def test_transform_url_with_default_tag(self):
        convert = loader.Loader("TAG").transform_url
        self.check_unchanging_urls(convert)
        eq = self.assertEqual
        # cvs:
        eq(convert("cvs://cvs.example.org/cvsroot:module"),
           "cvs://cvs.example.org/cvsroot:module:TAG")
        # repository:
        eq(convert("repository::"),
           "repository::TAG")
        eq(convert("repository:path"),
           "repository:path:TAG")
        eq(convert("repository:/some/path/:"),
           "repository:/some/path/:TAG")
        # Subversion:
        self.check_changing_subversion_urls("svn", "svn.example.org")
        self.check_changing_subversion_urls("svn+ssh", "svn.example.org")
        self.check_changing_subversion_urls("file", "",
                                            prefix=self.svnrepodir)
        self.check_changing_subversion_urls("file", "localhost",
                                            prefix=self.svnrepodir)

    def check_changing_subversion_urls(self, scheme, hostname, prefix=None):
        if not prefix:
            prefix = "/some/path/to/svnroot"
        convert = loader.Loader("TAG").transform_url
        eq = self.assertEqual
        def mkurl(path):
            return "%s://%s%s%s" % (scheme, hostname, prefix, path)
        eq(convert(mkurl("/tags/*/module/file.txt")),
           mkurl("/tags/TAG/module/file.txt"))

    def test_transform_url_without_default_tag(self):
        convert = loader.Loader().transform_url
        self.check_unchanging_urls(convert)
        eq = self.assertEqual

    def check_unchanging_urls(self, convert):
        eq = self.assertEqual
        eq(convert("http://example.org/foo/bar.txt"),
           "http://example.org/foo/bar.txt")
        eq(convert("https://example.org/foo/bar.txt"),
           "https://example.org/foo/bar.txt")
        eq(convert("file://localhost/path/to/somewhere.py"),
           "file://localhost/path/to/somewhere.py")
        eq(convert("file:///path/to/somewhere.py"),
           "file:///path/to/somewhere.py")
        eq(convert("cvs://cvs.example.org/cvsroot:path/:tag"),
           "cvs://cvs.example.org/cvsroot:path/:tag")
        eq(convert("repository:path/:tag"),
           "repository:path/:tag")
        eq(convert("repository:/some/path/:tag"),
           "repository:/some/path/:tag")
        eq(convert("svn://example.org/path/to/svnroot/tags/foo/file.txt"),
           "svn://example.org/path/to/svnroot/tags/foo/file.txt")
        eq(convert("svn://example.org/path/to/svnroot/branches/foo/file.txt"),
           "svn://example.org/path/to/svnroot/branches/foo/file.txt")
        eq(convert("svn+ssh://example.org/path/to/svnroot/tags/foo/file.txt"),
           "svn+ssh://example.org/path/to/svnroot/tags/foo/file.txt")
        eq(convert("svn+ssh://example.org/path/to/svnroot/branches/foo/file"),
           "svn+ssh://example.org/path/to/svnroot/branches/foo/file")
        # not really a URL, but a supported tagless thing
        eq(convert("local/path/reference.conf"),
           "local/path/reference.conf")

    def test_load_with_file(self):
        filename = os.path.abspath(__file__)
        URL = "file://" + urllib.pathname2url(filename)
        loader = self.createLoader()
        # Check that the file isn't copied if we don't ask for a mutable copy:
        p1 = loader.load(URL)
        self.assertEqual(p1, filename)
        # Check that we use the same copy if we ask again:
        p2 = loader.load(URL)
        self.assertEqual(p1, p2)

    def test_load_mutable_copy_with_file(self):
        filename = os.path.abspath(__file__)
        URL = "file://" + urllib.pathname2url(filename)
        loader = self.createLoader()
        # Check that the file isn't copied if we don't ask for a mutable copy:
        p1 = loader.load(URL)
        self.assertEqual(p1, filename)
        # Check that it is copied if we do:
        p2 = loader.load_mutable_copy(URL)
        self.assert_(filecmp.cmp(p1, filename, shallow=False))
        self.assertNotEqual(p1, p2)
        self.assert_(p2.startswith(tempfile.gettempdir()))
        # And check that it isn't copied again if we ask again:
        p3 = loader.load_mutable_copy(URL)
        self.assertEqual(p2, p3)
        loader.cleanup()

    def test_load_mutable_copy_with_directory(self):
        filename = os.path.abspath(__file__)
        filename = os.path.join(os.path.dirname(filename), "input")
        self.check_load_mutable_copy_with_directory(filename)

    def test_load_mutable_copy_with_directory_trailing_slash(self):
        filename = os.path.abspath(__file__)
        filename = os.path.join(os.path.dirname(filename), "input", "")
        self.check_load_mutable_copy_with_directory(filename)

    def check_load_mutable_copy_with_directory(self, filename):
        URL = "file://" + urllib.pathname2url(filename)
        loader = self.createLoader()
        # Check that the file isn't copied if we don't ask for a mutable copy:
        p1 = loader.load(URL)
        self.assertEqual(p1, filename)
        # Check that it is copied if we do:
        common_files = [
            "packages.map",
            "README.txt",
            "collection-1/DEPENDENCIES.cfg",
            "package/__init__.py",
            ]
        # Check that it is copied if we do:
        p2 = loader.load_mutable_copy(URL)
        self.assert_(filecmp.cmpfiles(p1, filename, common_files,
                                      shallow=False))
        self.assertNotEqual(p1, p2)
        self.assert_(p2.startswith(tempfile.gettempdir()))
        # And check that it isn't copied again if we ask again:
        p3 = loader.load_mutable_copy(URL)
        self.assertEqual(p2, p3)
        loader.cleanup()


class FileProxyLoader:

    cleanup_called = False

    def cleanup(self):
        self.cleanup_called += 1


class FileProxyTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = FileProxyLoader()
        self.mode = "rU"
        self.fp = loader.FileProxy(__file__, self.mode, self.loader)

    def tearDown(self):
        self.fp.close()

    def test_close(self):
        self.fp.close()
        self.assertEqual(self.loader.cleanup_called, 1)
        self.assert_(self.fp.closed)
        self.fp.close()
        self.assertEqual(self.loader.cleanup_called, 1)
        self.assert_(self.fp.closed)

    def test_softspace(self):
        self.failIf(self.fp.softspace)
        self.fp.softspace = 1
        self.assertEqual(self.fp.softspace, 1)
        self.fp.softspace = 2
        self.assertEqual(self.fp.softspace, 2)
        self.assertRaises(TypeError, setattr, self.fp, "softspace", "12")
        # XXX a little white box, to make sure softspace is passed to
        # the underlying file object:
        self.assertEqual(self.fp._file.softspace, 2)

    def test_read(self):
        text = self.fp.read()
        expected = open(__file__, self.mode).read()
        self.assertEqual(text, expected)

    def test_url_as_name(self):
        # make sure the path is used by default:
        self.assertEqual(self.fp.name, __file__)
        # now 
        fp = loader.FileProxy(__file__, self.mode, self.loader, "fake:url")
        try:
            self.assertEqual(fp.name, "fake:url")
        finally:
            fp.close()


def test_suite():
    suite = unittest.makeSuite(FileProxyTestCase)
    suite.addTest(unittest.makeSuite(LoaderTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
