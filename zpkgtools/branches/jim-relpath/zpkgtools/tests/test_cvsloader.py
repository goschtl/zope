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
"""Tests of zpkgtools.cvsloader."""

import doctest
import os.path
import shutil
import unittest

from StringIO import StringIO

from zpkgsetup.tests import tempfileapi as tempfile

from zpkgtools import cvsloader
from zpkgtools import loader
from zpkgtools.tests.test_loader import LoaderTestBase


class UrlUtilitiesTestCase(unittest.TestCase):

    def test_getCvsRoot(self):
        def check(cvsroot, *args, **kw):
            kw["path"] = "foo/bar"
            kw["password"] = "passwd"
            kw["tag"] = "TAG"  # should not show up in CVSROOT setting
            cvsurl = cvsloader.CvsUrl(*args, **kw)
            self.assertEqual(cvsurl.getCvsRoot(), cvsroot)

        check("/usr/local/cvsroot",
              None, None, "/usr/local/cvsroot")
        check(":ext:cvs.example.org:/cvsroot",
              "ext", "cvs.example.org", "/cvsroot")
        check(":ext:myuser@cvs.example.org:/cvsroot",
              "ext", "cvs.example.org", "/cvsroot", username="myuser")
        check(":pserver:cvs.example.org:/cvsroot",
              "pserver", "cvs.example.org", "/cvsroot")

    def test_cvs_getUrl(self):
        cvsurl = cvsloader.CvsUrl("", "cvs.example.org", "/cvsroot",
                                  "project/module")
        self.assertEqual(cvsurl.getUrl(),
                         "cvs://cvs.example.org/cvsroot:project/module")

        cvsurl.path = "module"
        cvsurl.tag = "TAG"
        self.assertEqual(cvsurl.getUrl(),
                         "cvs://cvs.example.org/cvsroot:module:TAG")

        cvsurl.username = "myuser"
        self.assertEqual(cvsurl.getUrl(),
                         "cvs://myuser@cvs.example.org/cvsroot:module:TAG")

        cvsurl.password = "pw"
        self.assertEqual(cvsurl.getUrl(),
                         "cvs://myuser:pw@cvs.example.org/cvsroot:module:TAG")

    def test_repository_getUrl(self):
        repo = cvsloader.RepositoryUrl("/absolute/path")
        self.assertEqual(repo.getUrl(), "repository:/absolute/path")
        repo.tag = "TAG"
        self.assertEqual(repo.getUrl(), "repository:/absolute/path:TAG")
        repo.path = None
        self.assertEqual(repo.getUrl(), "repository::TAG")
        repo.tag = None
        self.assertEqual(repo.getUrl(), "repository:")

    def test_repository_join_absolute_path(self):
        repo = cvsloader.RepositoryUrl("/absolute/path")
        cvsurl = cvsloader.CvsUrl("", "cvs.example.org", "/cvsroot",
                                  "project/module")
        result = cvsurl.join(repo)
        self.assert_(not result.type)
        self.assertEqual(result.host, "cvs.example.org")
        self.assertEqual(result.cvsroot, "/cvsroot")
        self.assertEqual(result.path, "absolute/path")
        self.assert_(not result.tag)

        cvsurl.tag = "TAG"
        result = cvsurl.join(repo)
        self.assert_(not result.type)
        self.assertEqual(result.host, "cvs.example.org")
        self.assertEqual(result.cvsroot, "/cvsroot")
        self.assertEqual(result.path, "absolute/path")
        self.assertEqual(result.tag, "TAG")

        repo.tag = "FOO"
        result = cvsurl.join(repo)
        self.assertEqual(result.path, "absolute/path")
        self.assertEqual(result.tag, "FOO")

        cvsurl.tag = None
        result = cvsurl.join(repo)
        self.assertEqual(result.path, "absolute/path")
        self.assertEqual(result.tag, "FOO")

    def test_repository_join_relative_path(self):
        repo = cvsloader.RepositoryUrl("relative/path")
        cvsurl = cvsloader.CvsUrl("", "cvs.example.org", "/cvsroot",
                                  "project/module")
        result = cvsurl.join(repo)
        self.assert_(not result.type)
        self.assertEqual(result.host, "cvs.example.org")
        self.assertEqual(result.cvsroot, "/cvsroot")
        self.assertEqual(result.path, "project/module/relative/path")
        self.assert_(not result.tag)

        cvsurl.tag = "TAG"
        result = cvsurl.join(repo)
        self.assert_(not result.type)
        self.assertEqual(result.host, "cvs.example.org")
        self.assertEqual(result.cvsroot, "/cvsroot")
        self.assertEqual(result.path, "project/module/relative/path")
        self.assertEqual(result.tag, "TAG")

        repo.tag = "FOO"
        result = cvsurl.join(repo)
        self.assertEqual(result.path, "project/module/relative/path")
        self.assertEqual(result.tag, "FOO")

        cvsurl.tag = None
        result = cvsurl.join(repo)
        self.assertEqual(result.path, "project/module/relative/path")
        self.assertEqual(result.tag, "FOO")

    def test_repository_join_without_path(self):
        repo = cvsloader.RepositoryUrl(None)
        cvsurl = cvsloader.CvsUrl("", "cvs.example.org", "/cvsroot",
                                  "project/module")
        result = cvsurl.join(repo)
        self.assert_(not result.type)
        self.assertEqual(result.host, "cvs.example.org")
        self.assertEqual(result.cvsroot, "/cvsroot")
        self.assertEqual(result.path, "project/module")
        self.assert_(not result.tag)

        cvsurl.tag = "TAG"
        result = cvsurl.join(repo)
        self.assert_(not result.type)
        self.assertEqual(result.host, "cvs.example.org")
        self.assertEqual(result.cvsroot, "/cvsroot")
        self.assertEqual(result.path, "project/module")
        self.assertEqual(result.tag, "TAG")

        repo.tag = "FOO"
        result = cvsurl.join(repo)
        self.assertEqual(result.path, "project/module")
        self.assertEqual(result.tag, "FOO")

        cvsurl.tag = None
        result = cvsurl.join(repo)
        self.assertEqual(result.path, "project/module")
        self.assertEqual(result.tag, "FOO")

    def test_parse_cvs(self):
        def check(url,
                  type, username, password, host, cvsroot, path, tag):
            cvsurl = cvsloader.parse(url)
            self.assert_(isinstance(cvsurl, cvsloader.CvsUrl))
            self.assertEqual(cvsurl.type, type)
            self.assertEqual(cvsurl.username, username)
            self.assertEqual(cvsurl.password, password)
            self.assertEqual(cvsurl.host, host)
            self.assertEqual(cvsurl.cvsroot, cvsroot)
            self.assertEqual(cvsurl.path, path)
            self.assertEqual(cvsurl.tag, tag)

        check("cvs://cvs.example.org:pserver/cvsroot:module/file.txt",
              "pserver", None, None, "cvs.example.org", "/cvsroot",
              "module/file.txt", None)

        check("CVS://user:pw@cvs.example.org:pserver/cvsroot/path:module/:TAG",
              "pserver", "user", "pw", "cvs.example.org", "/cvsroot/path",
              "module/", "TAG")

        # An empty path is ok; it means the same as "." (the whole repository)
        check("cvs://cvs.example.org:ext/cvsroot:",
              "ext", None, None, "cvs.example.org", "/cvsroot",
              "", None)

        # Empty username, password, type, and tag must be normalized to None:
        check("cvs://cvs.example.org/cvsroot:path:",
              None, None, None, "cvs.example.org", "/cvsroot",
              "path", None)

        # Local filesystem access to repository:
        check("cvs:///cvsroot:module/path/file.txt:TAG",
              None, None, None, None, "/cvsroot",
              "module/path/file.txt", "TAG")

        # Path within repository not specified; means the whole repository
        check("cvs://cvs.example.org:ext/cvsroot",
              "ext", None, None, "cvs.example.org", "/cvsroot",
              None, None)

        # Too many parts:
        self.assertRaises(ValueError,
                          cvsloader.parse,
                          "cvs://hostname/cvsroot:path:TAG:junk")

        # Can't generate a proper CVSROOT value:
        self.assertRaises(ValueError,
                          cvsloader.parse, "cvs://")

    def test_parse_repository(self):
        def check(url, path, tag):
            cvsurl = cvsloader.parse(url)
            self.assert_(isinstance(cvsurl, cvsloader.RepositoryUrl))
            self.assertEqual(cvsurl.path, path)
            self.assertEqual(cvsurl.tag, tag)

        check("repository:path/to/some/file.txt",
              "path/to/some/file.txt", None)

        check("repository:/some/path/",
              "/some/path/", None)

        check("repository:path/to/some/file.txt:TAG",
              "path/to/some/file.txt", "TAG")

        check("repository:/some/path/:TAG",
              "/some/path/", "TAG")

        check("repository::TAG",
              None, "TAG")

        check("repository::",
              None, None)

        check("repository:",
              None, None)

        # Too many parts:
        self.assertRaises(ValueError,
                          cvsloader.parse, "repository:path:TAG:junk")

    def test_parse_invalid(self):
        # Scheme isn't "cvs" or "repository":
        self.assertRaises(ValueError,
                          cvsloader.parse, "http://www.example.org/")


class CvsWorkingDirectoryBase(LoaderTestBase):

    def initialize(self, root, repository, tag=None):
        self.writeCvsFile("Root", root + "\n")
        self.writeCvsFile("Repository", repository + "\n")
        if tag:
            # `tag` should include the D, N, or T prefix letter
            self.writeCvsFile("Tag", tag + "\n")

    def writeCvsFile(self, name, content):
        f = open(os.path.join(self.cvsdir, name), "w")
        f.write(content)
        f.close()


class CvsWorkingDirectoryTestCase(CvsWorkingDirectoryBase):

    def setUp(self):
        super(CvsWorkingDirectoryTestCase, self).setUp()
        self.filename = os.path.join(self.workingdir, "file.txt")
        f = open(self.filename, "w")
        f.close()

    def check(self, filename,
              type, username, password, host, cvsroot, path, tag):
        cvsurl = cvsloader.fromPath(filename)
        self.assertEqual(cvsurl.type, type)
        self.assertEqual(cvsurl.username, username)
        self.assertEqual(cvsurl.password, password)
        self.assertEqual(cvsurl.host, host)
        self.assertEqual(cvsurl.cvsroot, cvsroot)
        self.assertEqual(cvsurl.path, path)
        self.assertEqual(cvsurl.tag, tag)

    # tests

    def test_without_tag(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package")
        # Check the directory itself:
        self.check(self.workingdir,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/", None)
        # And for a contained file:
        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", None)

    def test_with_branch_tag(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "TTAG")
        # Check the directory itself:
        self.check(self.workingdir,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/", "TAG")
        # And for a contained file:
        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "TAG")

    def test_with_nonbranch_tag(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "NTAG")
        # Check the directory itself:
        self.check(self.workingdir,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/", "TAG")
        # And for a contained file:
        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "TAG")

    def test_without_username(self):
        self.initialize(":ext:myuser@cvs.example.org:/cvsroot",
                        "module/package")
        self.check(self.workingdir,
                   "ext", "myuser", None, "cvs.example.org", "/cvsroot",
                   "module/package/", None)

    def test_with_entries_branch(self):
        # Test with a branch tag override for one file.
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package")
        self.writeCvsFile(
            "Entries",
            "/file.txt/1.2.2.8/Mon Mar  1 23:00:24 2004/-kk/Tnew-tag\n")

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "new-tag")

    def test_with_entries_tag(self):
        # Test with a non-branch tag override for one file.
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "NTAG")
        self.writeCvsFile(
            "Entries",
            "/file.txt/1.2.2.8/Mon Mar  1 23:00:24 2004/-kk/Nnew-tag\n")

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "new-tag")

    def test_with_date_and_entries_tag(self):
        # Test with a non-branch tag override for one file.
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "D2004.02.28.04.00.00")
        self.writeCvsFile(
            "Entries",
            "/file.txt/1.2.2.8/Mon Mar  1 23:00:24 2004/-kk/Nnew-tag\n")

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "new-tag")

    def test_with_tag_and_entries_date(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "TTAG")
        self.writeCvsFile("Entries",
                          ("/file.txt/1.2.2.8/Mon Mar  1 23:00:24 2004/-kk/"
                           "D2004.02.28.04.00.00\n"))

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "TAG")

    def test_with_entries_date(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package")
        self.writeCvsFile("Entries",
                          ("/file.txt/1.1/Mon Mar  1 23:00:24 2004/-kk/"
                           "D2004.02.28.04.00.00\n"))

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", None)

    def test_without_cvs_info(self):
        # make sure fromPath() returns None if there's no CVS metadata
        os.rmdir(self.cvsdir)
        cvsurl = cvsloader.fromPath(self.filename)
        self.assert_(cvsurl is None)


class CvsLoaderTestCase(unittest.TestCase):

    """Tests for the CVS loader itself.

    These tests verify that the runCvsExport() method is called with
    the expected information, not that runCvsExport() is actually
    doing to right thing.  This does not assume that any CVS
    repositories are actually available.
    """

    cvs_return_code = 0
    rlog_output = ""

    def setUp(self):
        self._temp_working_dir = tempfile.mkdtemp(prefix="test-workdir-")

    def tearDown(self):
        shutil.rmtree(self._temp_working_dir)

    def runCvsExport(self, cvsroot, workdir, tag, path):
        self.assert_(os.path.isdir(workdir),
                     "working directory must exist and be a directory")
        self.cvsroot = cvsroot
        self.workdir = workdir
        self.tag = tag
        self.path = path
        return self.cvs_return_code

    def openCvsRLog(self, cvsroot, path):
        # XXX This assumes that os.popen() is used to get CVS output,
        # but ensures that the generation of the command string
        # doesn't fail in simple ways.
        self.rlog_cvsroot = cvsroot
        self.rlog_path = path
        os_popen = os.popen
        os.popen = self.popen
        try:
            return self.loader.__class__.openCvsRLog(
                self.loader, cvsroot, path)
        finally:
            os.popen = os_popen

    def popen(self, command, mode="r"):
        self.rlog_command = command
        return StringIO(self.rlog_output)

    def createLoader(self):
        """Create a loader that won't actually access CVS."""
        loader = cvsloader.CvsLoader()
        self.loader = loader
        loader.runCvsExport = self.runCvsExport
        loader.openCvsRLog = self.openCvsRLog
        return loader

    # tests

    def test_simple_load_ok(self):
        self.rlog_output = "/cvsroot/module/dir/README.txt,v\n"
        loader = self.createLoader()
        path = loader.load(
            cvsloader.parse("cvs://cvs.example.org:ext/cvsroot:module/dir"),
            self._temp_working_dir)
        self.assertEqual(self.cvsroot, ":ext:cvs.example.org:/cvsroot")
        self.assertEqual(self.tag, "HEAD")
        self.assertEqual(self.path, "module/dir")
        self.assert_(os.path.isdir(self.workdir),
                     "working directory must exist after a successful run")
        self.assertEqual(self.rlog_cvsroot, self.cvsroot)
        self.assertEqual(self.rlog_path, self.path)

    def test_simple_load_error(self):
        self.cvs_return_code = 1
        url = "cvs://cvs.example.org:ext/cvsroot:module/dir"
        loader = self.createLoader()
        try:
            loader.load(cvsloader.parse(url), self._temp_working_dir)
        except cvsloader.CvsLoadingError, e:
            self.assertEqual(e.exitcode, self.cvs_return_code)
            self.assertEqual(e.cvsurl.getUrl(), url)
        else:
            self.fail("expected CvsLoadingError")
        self.assertEqual(self.cvsroot, ":ext:cvs.example.org:/cvsroot")
        self.assertEqual(self.tag, "HEAD")
        self.assertEqual(self.path, "module/dir")

    def test_reuse_loaded_resource(self):
        url = "cvs://cvs.example.org/cvsroot:module/path"
        myloader = loader.Loader()
        myloader.cvsloader = self.createLoader()
        first = myloader.load(url)
        second = myloader.load(url)
        self.assertEqual(first, second)

    def test_no_reuse_loaded_resource_different_tags(self):
        url = "cvs://cvs.example.org/cvsroot:module/path"
        myloader = loader.Loader()
        myloader.cvsloader = self.createLoader()
        first = myloader.load(url)
        second = myloader.load(url + ":TAG")
        self.assertNotEqual(first, second)

    def test_isFileResource_file(self):
        self.check_isFileResource("/cvsroot/module/FOO,v\n",
                                  True)

    def test_isFileResource_file_in_attic(self):
        self.check_isFileResource("/cvsroot/module/Attic/FOO,v\n",
                                  True)

    def test_isFileResource_directory(self):
        self.check_isFileResource("/cvsroot/module/FOO/FILE.txt,v\n"
                                  "/cvsroot/module/FOO/README.txt,v\n",
                                  False)

    def check_isFileResource(self, rlog_output, expected_result):
        self.rlog_output = rlog_output
        loader = self.createLoader()
        cvsurl = cvsloader.parse(
            "cvs://user@cvs.example.org:pserver/cvsroot:module/FOO:TAG")
        self.assertEqual(not not loader.isFileResource(cvsurl),
                         expected_result)
        self.assertEqual(self.rlog_path, "module/FOO")
        self.assertEqual(self.rlog_cvsroot,
                         ":pserver:user@cvs.example.org:/cvsroot")


def test_suite():
    suite = unittest.makeSuite(UrlUtilitiesTestCase)
    suite.addTest(unittest.makeSuite(CvsWorkingDirectoryTestCase))
    suite.addTest(unittest.makeSuite(CvsLoaderTestCase))
    suite.addTest(doctest.DocTestSuite("zpkgtools.cvsloader"))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
