##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for the Network class.

$Id: test_network.py,v 1.3 2003/05/15 20:03:05 gvanrossum Exp $
"""

import os
import shutil
import unittest
import tempfile

from StringIO import StringIO

from os.path import isdir, isfile, join

from zope.fssync.fssync import Network, Error

sample_rooturl = "http://user:passwd@host:8080/path"

class TestNetwork(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.network = Network()
        # Create a list of temporary files to clean up at the end
        self.tempfiles = []

    def tearDown(self):
        # Clean up temporary files (or directories)
        for fn in self.tempfiles:
            if isdir(fn):
                shutil.rmtree(fn)
            elif isfile(fn):
                os.remove(fn)
        unittest.TestCase.tearDown(self)

    def adddir(self):
        # Create and register a temporary directory
        dir = tempfile.mktemp()
        self.tempfiles.append(dir)
        os.mkdir(dir)
        return dir

    def cmpfile(self, file1, file2, mode="r"):
        # Compare two files; they must exist
        f1 = open(file1, mode)
        try:
            data1 = f1.read()
        finally:
            f1.close()
        f2 = open(file2, mode)
        try:
            data2 = f2.read()
        finally:
            f2.close()
        return data1 == data2

    def test_initial_state(self):
        self.assertEqual(self.network.rooturl, None)
        self.assertEqual(self.network.roottype, None)
        self.assertEqual(self.network.rootpath, None)
        self.assertEqual(self.network.user_passwd, None)
        self.assertEqual(self.network.host_port, None)

    def test_setrooturl(self):
        self.network.setrooturl(sample_rooturl)
        self.assertEqual(self.network.rooturl, sample_rooturl)
        self.assertEqual(self.network.roottype, "http")
        self.assertEqual(self.network.rootpath, "/path")
        self.assertEqual(self.network.user_passwd, "user:passwd")
        self.assertEqual(self.network.host_port, "host:8080")

    def test_setrooturl_nopath(self):
        rooturl = "http://user:passwd@host:8080"
        self.network.setrooturl(rooturl)
        self.assertEqual(self.network.rooturl, rooturl)
        self.assertEqual(self.network.roottype, "http")
        self.assertEqual(self.network.rootpath, "/")
        self.assertEqual(self.network.user_passwd, "user:passwd")
        self.assertEqual(self.network.host_port, "host:8080")

    def test_findrooturl_notfound(self):
        # XXX This test will fail if a file /tmp/@@Zope/Root exists :-(
        target = self.adddir()
        self.assertEqual(self.network.findrooturl(target), None)

    def test_findrooturl_found(self):
        target = self.adddir()
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        rootfile = join(zdir, "Root")
        f = open(rootfile, "w")
        f.write(sample_rooturl + "\n")
        f.close()
        self.assertEqual(self.network.findrooturl(target), sample_rooturl)

    def test_saverooturl(self):
        self.network.setrooturl(sample_rooturl)
        target = self.adddir()
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        rootfile = join(zdir, "Root")
        self.network.saverooturl(target)
        f = open(rootfile, "r")
        data = f.read()
        f.close()
        self.assertEqual(data.strip(), sample_rooturl)

    def test_loadrooturl(self):
        target = self.adddir()
        self.assertRaises(Error, self.network.loadrooturl, target)
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        self.network.setrooturl(sample_rooturl)
        self.network.saverooturl(target)
        new = Network()
        new.loadrooturl(target)
        self.assertEqual(new.rooturl, sample_rooturl)

    def test_httpreq(self):
        # XXX I don't want to write up a dummy server just to test
        # this so I'll just send a request to python.org that I know
        # will fail.
        self.network.setrooturl("http://python.org")
        self.assertRaises(Error, self.network.httpreq, "/xyzzy", "@@view")

    def test_slurptext_html(self):
        fp = StringIO("<p>This is some\n\ntext.</p>\n")
        result = self.network.slurptext(fp, {"Content-type": "text/html"})
        self.assertEqual(result, "This is some text.")

    def test_slurptext_plain(self):
        fp = StringIO("<p>This is some\n\ntext.</p>\n")
        result = self.network.slurptext(fp, {"Content-type": "text/plain"})
        self.assertEqual(result, "<p>This is some\n\ntext.</p>")

    def test_slurptext_nontext(self):
        fp = StringIO("<p>This is some\n\ntext.</p>\n")
        result = self.network.slurptext(fp, {"Content-type": "foo/bar"})
        self.assertEqual(result, "Content-type: foo/bar")

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestNetwork)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
