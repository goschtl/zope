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
        self.writeFile(name, text)
        self.writeFile(os.path.join(".svn", "text-base", name + ".svn-base"),
                       text)
        self.writeFile(os.path.join(".svn", "prop-base", name + ".svn-base"),
                       "END\n")
        self.writeFile(os.path.join(".svn", "props", name + ".svn-work"),
                       "END\n")

    def writeFile(self, name, text):
        """Write a file within the simulated checkout."""
        f = open(os.path.join(self.svnworkdir, name), "w")
        f.write(text)
        f.close()


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


class SubversionFileUrlTestCase(SubversionLocalRepositoryBase,
                                SubversionUrlTestCase):
    """Test handling of file:///... URLs."""


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
