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
"""Tests of zpkgtools.svnloader."""

import os
import shutil
import tempfile
import unittest

from zpkgtools import cvsloader
from zpkgtools import svnloader


class SubversionRepositoryBase(unittest.TestCase):
    """Mix-in test support class that provides a fake Subversion repository.

    :ivar repodir: Directory containing the fake repository.

    """

    def setUp(self):
        super(SubversionRepositoryBase, self).setUp()
        self.svnrepodir = tempfile.mkdtemp()
        os.mkdir(os.path.join(self.svnrepodir, "conf"))
        os.mkdir(os.path.join(self.svnrepodir, "dav"))
        os.mkdir(os.path.join(self.svnrepodir, "db"))
        os.mkdir(os.path.join(self.svnrepodir, "hooks"))
        os.mkdir(os.path.join(self.svnrepodir, "locks"))
        open(os.path.join(self.svnrepodir, "db", "DB_CONFIG"), "w").close()

    def tearDown(self):
        super(SubversionRepositoryBase, self).tearDown()
        shutil.rmtree(self.svnrepodir)


class SubversionUrlTestCase(unittest.TestCase):
    """Test handling of svn://host/... URLs."""

    TYPE = "svn"
    HOSTPART = "svn.example.com"
    SVNROOT = "/path/to/repo"

    def mkurl(self, path):
        return "%s://%s%s%s" % (self.TYPE, self.HOSTPART, self.SVNROOT, path)

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

    def test_join(self):
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


class SubversionSshUrlTestCase(SubversionUrlTestCase):
    """Test handling of svn+ssh://host/... URLs."""

    TYPE = "svn+ssh"
    HOSTPART = "svn.example.com"


class SubversionFileUrlTestCase(SubversionRepositoryBase,
                                SubversionUrlTestCase):
    """Test handling of file:///... URLs."""

    # We create a "stub" repository so is_subversion_url() can
    # determine whether a file: URL points into Subversion.
    #
    # XXX Can we assume svnadmin is available locally?  Probably not.

    TYPE = "file"
    HOSTPART = ""

    def setUp(self):
        super(SubversionFileUrlTestCase, self).setUp()
        parts = self.svnrepodir.split(os.sep)
        self.SVNROOT = "/".join(parts)


class SubversionLocalhostFileUrlTestCase(SubversionFileUrlTestCase):
    """Test handling of file://localhost/... URLs."""

    HOSTPART = "localhost"


def test_suite():
    suite = unittest.makeSuite(SubversionUrlTestCase)
    suite.addTest(unittest.makeSuite(SubversionSshUrlTestCase))
    suite.addTest(unittest.makeSuite(SubversionFileUrlTestCase))
    suite.addTest(unittest.makeSuite(SubversionLocalhostFileUrlTestCase))
    return suite

if __name__ == "__main__":
    unittest.main(defaultTest="test_suite")
