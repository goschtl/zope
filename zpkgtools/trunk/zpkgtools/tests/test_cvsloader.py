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
"""Tests of zpkgtools.cvsloader."""

import os.path
import shutil
import tempfile
import unittest

from StringIO import StringIO

from zpkgtools import cvsloader


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


class CvsWorkingDirectoryBase(unittest.TestCase):

    def setUp(self):
        self.workingdir = tempfile.mkdtemp(prefix="test-workdir-")
        self.cvsdir = os.path.join(self.workingdir, "CVS")
        os.mkdir(self.cvsdir)

    def tearDown(self):
        shutil.rmtree(self.workingdir)

    def initialize(self, root, repository, tag=None):
        self.writeCvsFile("Root", root + "\n")
        self.writeCvsFile("Repository", repository + "\n")
        if tag:
            self.writeCvsFile("Tag", "T%s\n" % tag)

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

    def test_with_tag(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "TAG")
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

    def test_with_entries_override(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package")
        self.writeCvsFile(
            "Entries",
            "/file.txt/1.2.2.8/Mon Mar  1 23:00:24 2004/-kk/Tnew-tag\n")

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "new-tag")

    def test_with_entries_tag(self):
        self.initialize(":ext:cvs.example.org:/cvsroot",
                        "module/package",
                        "TAG")
        self.writeCvsFile(
            "Entries",
            "/file.txt/1.2.2.8/Mon Mar  1 23:00:24 2004/-kk/Tnew-tag\n")

        self.check(self.filename,
                   "ext", None, None, "cvs.example.org", "/cvsroot",
                   "module/package/file.txt", "new-tag")


class CvsLoaderTestCase(unittest.TestCase):

    """Tests for the CVS loader itself.

    These tests verify that the runCvsExport() method is called with
    the expected information, not that runCvsExport() is actually
    doing to right thing.  This does not assume that any CVS
    repositories are actually available.
    """

    cvs_return_code = 0
    rlog_output = ""

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

    def createLoader(self, baseurl):
        """Create a loader that won't actually access CVS."""
        loader = cvsloader.CvsLoader(baseurl)
        self.loader = loader
        loader.runCvsExport = self.runCvsExport
        loader.openCvsRLog = self.openCvsRLog
        return loader

    # tests

    def test_simple_load_ok(self):
        self.rlog_output = "/cvsroot/module/dir/README.txt,v\n"
        baseurl = cvsloader.parse(
            "cvs://cvs.example.org:ext/cvsroot:module/dir")
        loader = self.createLoader(baseurl)
        path = loader.load("repository:")
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
        baseurl = cvsloader.parse(url)
        loader = self.createLoader(baseurl)
        try:
            loader.load("repository:")
        except cvsloader.CvsLoadingError, e:
            self.assertEqual(e.exitcode, self.cvs_return_code)
            self.assertEqual(e.cvsurl.getUrl(), url)
        else:
            self.fail("expected CvsLoadingError")
        self.assertEqual(self.cvsroot, ":ext:cvs.example.org:/cvsroot")
        self.assertEqual(self.tag, "HEAD")
        self.assertEqual(self.path, "module/dir")
        self.assert_(not os.path.exists(self.workdir),
                     "working directory must not exist after a failed run")

    def test_reuse_loaded_resource(self):
        url = "cvs://cvs.example.org/cvsroot:module/path"
        loader = self.createLoader(None)
        first = loader.load(url)
        second = loader.load(url)
        self.assertEqual(first, second)

    def test_no_reuse_loaded_resource_different_tags(self):
        url = "cvs://cvs.example.org/cvsroot:module/path"
        loader = self.createLoader(None)
        first = loader.load(url)
        second = loader.load(url + ":TAG")
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
        baseurl = cvsloader.parse(
            "cvs://user@cvs.example.org:pserver/cvsroot:module")
        loader = self.createLoader(baseurl)
        repourl = cvsloader.parse("repository:FOO:TAG")
        self.assertEqual(not not loader.isFileResource(repourl),
                         expected_result)
        self.assertEqual(self.rlog_path, "module/FOO")
        self.assertEqual(self.rlog_cvsroot,
                         ":pserver:user@cvs.example.org:/cvsroot")


class DummyLoader:

    cleanup_called = False

    def cleanup(self):
        self.cleanup_called += 1


class FileProxyTestCase(unittest.TestCase):

    def setUp(self):
        self.loader = DummyLoader()
        self.mode = "rU"
        self.fp = cvsloader.FileProxy(__file__, self.mode, self.loader)

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
        fp = cvsloader.FileProxy(__file__, self.mode, self.loader, "fake:url")
        try:
            self.assertEqual(fp.name, "fake:url")
        finally:
            fp.close()


def test_suite():
    suite = unittest.makeSuite(UrlUtilitiesTestCase)
    suite.addTest(unittest.makeSuite(CvsWorkingDirectoryTestCase))
    suite.addTest(unittest.makeSuite(CvsLoaderTestCase))
    suite.addTest(unittest.makeSuite(FileProxyTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
