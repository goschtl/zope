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
"""Tests of zpkgtools.svnloader."""

import os
import shutil
import unittest

from zpkgsetup import urlutils
from zpkgsetup.tests import tempfileapi as tempfile

from zpkgtools import cvsloader
from zpkgtools import svnloader


class SubversionTestBase(unittest.TestCase):
    """Base class for the Subversion-related tests.

    This provides a simple helper method that relies on the setting of
    some instance variables.  These are most often specified as class
    attributes.

    :ivar TYPE: The scheme of the Subversion repository to work with.

    :ivar HOSTPART: The host portion of the Subversion URL.  This may
      be an empty string for file:/// URLs.

    :ivar SVNROOT: The path to the repository on the server host in
      POSIX notation.  A default dummy value is provided, suitable for
      non-file:// repository URLs.

    """

    SVNROOT = "/path/to/repo"

    def mkurl(self, path):
        return "%s://%s%s%s" % (self.TYPE, self.HOSTPART, self.SVNROOT, path)


class SubversionLocalRepositoryBase(SubversionTestBase):
    """Mix-in test support class that provides a fake Subversion repository.

    :ivar svnrepodir: Directory containing the fake repository.

    """

    TYPE = "file"
    HOSTPART = ""

    def mkurl(self, path):
        root = urlutils.pathname2url(self.SVNROOT)
        return "file://%s%s%s" % (self.HOSTPART, root, path)

    def setUp(self):
        super(SubversionLocalRepositoryBase, self).setUp()
        self.svnrepodir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.svnrepodir, "conf"))
        os.mkdir(os.path.join(self.svnrepodir, "dav"))
        os.mkdir(os.path.join(self.svnrepodir, "db"))
        os.mkdir(os.path.join(self.svnrepodir, "hooks"))
        os.mkdir(os.path.join(self.svnrepodir, "locks"))
        open(os.path.join(self.svnrepodir, "db", "DB_CONFIG"), "w").close()
        self.SVNROOT = self.svnrepodir.replace(os.sep, "/")

    def tearDown(self):
        super(SubversionLocalRepositoryBase, self).tearDown()
        shutil.rmtree(self.svnrepodir)


class SubversionWorkingDirBase(SubversionTestBase):
    """Mix-in test support class that provides a fake Subversion
    working directory (checkout).

    :ivar svnworkdir: Directory containing the simulated checkout.

    :ivar svndir: .svn/ directory in the simulated checkout.

    """

    def setUp(self):
        super(SubversionWorkingDirBase, self).setUp()
        self.svnworkdir = tempfile.mkdtemp()
        self.svndir = os.path.join(self.svnworkdir, ".svn")
        os.mkdir(self.svndir)
        os.mkdir(os.path.join(self.svndir, "tmp"))
        self.writeSvnMetafile("format", "4\n")
        self.writeSvnMetafile("empty-file", "")
        self.writeSvnMetafile("README.txt", "Yeah, there's a readme file.\n")
        for dn in ("prop-base", "props", "text-base", "wcprops"):
            os.mkdir(os.path.join(self.svndir, dn))
            os.mkdir(os.path.join(self.svndir, "tmp", dn))

    def tearDown(self):
        super(SubversionWorkingDirBase, self).tearDown()
        shutil.rmtree(self.svnworkdir)

    def writeSvnMetafile(self, name, text):
        """Write a file directly in the .svn/ directory."""
        self.writeFile(os.path.join(".svn", name), text)

    def writeSvnUserfile(self, name, text, **kw):
        """Write a user file and the simplest Subversion support files.

        This does not add an entry to .svn/entries for the new file.
        """
        path = self.writeFile(name, text)
        self.writeFile(os.path.join(".svn", "text-base", name + ".svn-base"),
                       text)
        self.writeFile(os.path.join(".svn", "prop-base", name + ".svn-base"),
                       "END\n")
        self.writeFile(os.path.join(".svn", "props", name + ".svn-work"),
                       "END\n")
        return path

    def writeFile(self, name, text):
        """Write a file within the simulated checkout."""
        path = os.path.join(self.svnworkdir, name)
        f = open(path, "w")
        f.write(text)
        f.close()
        return path


class SubversionUrlTestCase(SubversionTestBase):
    """Test handling of svn://host/... URLs."""

    TYPE = "svn"
    HOSTPART = "svn.example.com"

    def test_parse_round_trip(self):
        def check(path):
            url = self.mkurl(path)
            svnurl = svnloader.parse(url)
            self.assertEqual(url, svnurl.getUrl())

        # "tagless" flavor; they don't conform to the convention for tagging
        check("/some/path.txt")
        # tagless but conventional: this represent a branch
        check("/branches/B1/some/path.txt")

    def test_parse_splits_right(self):
        def split(path):
            url = self.mkurl(path)
            svnurl = svnloader.parse(url)
            prefix = self.mkurl("")
            self.assert_(svnurl.prefix.startswith(prefix))
            return svnurl.prefix[len(prefix):], svnurl.tail, svnurl.tag
        eq = self.assertEqual
        eq(split("/trunk/file.txt"),    ("", "file.txt", "HEAD"))
        eq(split("/tags/foo/file.txt"), ("", "file.txt", "foo"))
        eq(split("/tags/*/file.txt"),   ("", "file.txt", None))

    def test_join_with_path(self):
        URL = self.mkurl("/tags/*/path")
        repo = cvsloader.parse("repository:more/path")
        svnurl = svnloader.parse(URL)
        newurl = svnurl.join(repo)
        self.assertEqual(newurl.tag, None)
        self.assertEqual(newurl.prefix, self.mkurl(""))
        self.assertEqual(newurl.tail, "path/more/path")

    def test_join_with_path_and_new_tag(self):
        eq = self.assertEqual

        URL = self.mkurl("/tags/*/path")
        repo = cvsloader.parse("repository:more/path:TAG")
        svnurl = svnloader.parse(URL)
        newurl = svnurl.join(repo)
        eq(newurl.tag, "TAG")
        eq(newurl.prefix, self.mkurl(""))
        eq(newurl.tail, "path/more/path")
        eq(newurl.getUrl(), self.mkurl("/tags/TAG/path/more/path"))

        repo = cvsloader.parse("repository:more/path:HEAD")
        svnurl = svnloader.parse(URL)
        newurl = svnurl.join(repo)
        eq(newurl.tag, "HEAD")
        eq(newurl.prefix, self.mkurl(""))
        eq(newurl.tail, "path/more/path")
        eq(newurl.getUrl(), self.mkurl("/trunk/path/more/path"))

    def test_join_with_just_new_tag(self):
        eq = self.assertEqual
        svnroot = self.mkurl("")

        # join with a changed tag:
        URL = self.mkurl("/tags/*/file.txt")
        repo = cvsloader.parse("repository::FOO")
        svnurl = svnloader.parse(URL)
        newurl = svnurl.join(repo)
        eq(newurl.tag, "FOO")
        eq(newurl.prefix, svnroot)
        eq(newurl.tail, "file.txt")
        eq(newurl.getUrl(), self.mkurl("/tags/FOO/file.txt"))

        # join, changing the tag to the HEAD:
        URL = self.mkurl("/tags/*/file.txt")
        repo = cvsloader.parse("repository::HEAD")
        svnurl = svnloader.parse(URL)
        newurl = svnurl.join(repo)
        eq(newurl.tag, "HEAD")
        eq(newurl.prefix, svnroot)
        eq(newurl.tail, "file.txt")
        eq(newurl.getUrl(), self.mkurl("/trunk/file.txt"))

        # join, changing the tag from the HEAD:
        URL = self.mkurl("/trunk/file.txt")
        repo = cvsloader.parse("repository::FOO")
        svnurl = svnloader.parse(URL)
        newurl = svnurl.join(repo)
        eq(newurl.tag, "FOO")
        eq(newurl.prefix, svnroot)
        eq(newurl.tail, "file.txt")
        eq(newurl.getUrl(), self.mkurl("/tags/FOO/file.txt"))

    def test_is_subversion_url(self):
        note = " (repo in %s)" % self.SVNROOT
        def check(path):
            # what's expected to pass:
            url = self.mkurl(path)
            self.assert_(svnloader.is_subversion_url(url), url + note)
            # invalid scheme:
            url = "x" + url
            self.assert_(not svnloader.is_subversion_url(url), url + note)
        check("")
        check("/")
        check("/foo/bar")
        check("/foo/bar/")
        check("/foo/bar.txt")
        check("/trunk/foo/bar.txt")
        check("/tags/foobar/foo/bar.txt")
        check("/branches/foobar/foo/bar.txt")
        # Things that don't look like URLs at all:
        self.assert_(not svnloader.is_subversion_url("some/path"))
        self.assert_(not svnloader.is_subversion_url("/some/path"))
        self.assert_(not svnloader.is_subversion_url("/"))
        self.assert_(not svnloader.is_subversion_url("/foo.txt"))
        self.assert_(not svnloader.is_subversion_url("foo/"))


class SubversionSshUrlTestCase(SubversionUrlTestCase):
    """Test handling of svn+ssh://host/... URLs."""

    TYPE = "svn+ssh"


class SubversionPlusSpecialUrlTestCase(SubversionUrlTestCase):
    """Test handling of svn+other://host/... URLs."""

    TYPE = "svn+other"


class SubversionFileUrlTestCase(SubversionLocalRepositoryBase,
                                SubversionUrlTestCase):
    """Test handling of file:///... URLs."""

    def mkurl(self, path):
        root = urlutils.pathname2url(self.SVNROOT)
        return "file://%s%s%s" % (self.HOSTPART, root, path)


class SubversionLocalhostFileUrlTestCase(SubversionFileUrlTestCase):
    """Test handling of file://localhost/... URLs."""

    HOSTPART = "localhost"


class FromPathTestCase(SubversionWorkingDirBase):
    """Tests of the zpkgtools.svnloader.fromPath() function."""

    def test_fromPath_without_subversion_working_dir(self):
        # remove the .svn directory to disassociate with Subversion
        shutil.rmtree(self.svndir)
        self.assert_(svnloader.fromPath(self.svnworkdir) is None)
        filename = self.writeFile("file.txt", "phooey!")
        self.assert_(svnloader.fromPath(filename) is None)

    def test_fromPath_with_directory(self):
        self.writeSvnMetafile("entries", SUBVERSION_ENTRIES_FILE)
        svnurl = svnloader.fromPath(self.svnworkdir)
        self.assertEqual(svnurl.tag, "HEAD")
        self.assertEqual(svnurl.tail, "")
        self.assertEqual(svnurl.prefix,
                         "svn+ssh://svn.example.org/repos/main/ZConfig")

    def test_fromPath_with_file(self):
        self.writeSvnMetafile("entries", SUBVERSION_ENTRIES_FILE)
        path = self.writeSvnUserfile("SETUP.cfg", "# yee haw!\n")
        svnurl = svnloader.fromPath(path)
        self.assertEqual(svnurl.tag, "HEAD")
        self.assertEqual(svnurl.tail, "SETUP.cfg")
        self.assertEqual(svnurl.prefix,
                         "svn+ssh://svn.example.org/repos/main/ZConfig")

    def test_fromPath_with_unregistered_directory(self):
        # an unregistered directory should look exactly like a
        # directory that isn't related to Subversion at all, so let's
        # check that:
        self.writeSvnMetafile("entries", SUBVERSION_ENTRIES_FILE)
        path = os.path.join(self.svnworkdir, "splat")
        os.mkdir(path)
        self.assert_(svnloader.fromPath(path) is None)

    def test_fromPath_with_unregistered_file(self):
        self.writeSvnMetafile("entries", SUBVERSION_ENTRIES_FILE)
        path = self.writeSvnUserfile("file.txt", "# yee haw!\n")
        self.assert_(svnloader.fromPath(path) is None)


# This sample of a .svn/entries file was derived from one of the test
# repositories built while evaluating use of Subversion for the
# zope.org codebase; the host names have been modified.
#
SUBVERSION_ENTRIES_FILE = '''\
<?xml version="1.0" encoding="utf-8"?>
<wc-entries
   xmlns="svn:">
<entry
   committed-rev="24339"
   name=""
   committed-date="2004-05-05T06:57:11.458839Z"
   url="svn+ssh://svn.example.org/repos/main/ZConfig/trunk"
   last-author="fdrake"
   kind="dir"
   uuid="d01a3465-94d9-0310-b8d5-84ac064563bc"
   revision="24339"/>
<entry
   committed-rev="24338"
   name="SETUP.cfg"
   text-time="2004-05-05T06:42:32.000000Z"
   committed-date="2004-05-05T06:46:17.523287Z"
   checksum="5d4b02a83e1af0e7bb5bd339a3b5cf9f"
   last-author="fdrake"
   kind="file"
   prop-time="2004-05-05T06:24:05.000000Z"/>
</wc-entries>
'''


def test_suite():
    suite = unittest.makeSuite(SubversionUrlTestCase)
    suite.addTest(unittest.makeSuite(SubversionSshUrlTestCase))
    suite.addTest(unittest.makeSuite(SubversionPlusSpecialUrlTestCase))
    suite.addTest(unittest.makeSuite(SubversionFileUrlTestCase))
    suite.addTest(unittest.makeSuite(SubversionLocalhostFileUrlTestCase))
    suite.addTest(unittest.makeSuite(FromPathTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
