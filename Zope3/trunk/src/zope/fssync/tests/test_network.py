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

$Id: test_network.py,v 1.4 2003/05/28 14:40:04 gvanrossum Exp $
"""

import os
import unittest

from StringIO import StringIO

from os.path import isdir, isfile, join

from zope.fssync.fssync import Network, Error
from zope.fssync.tests.tempfiles import TempFiles

sample_rooturl = "http://user:passwd@host:8080/path"

class TestNetwork(TempFiles):

    def setUp(self):
        TempFiles.setUp(self)
        self.network = Network()

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
        target = self.tempdir()
        self.assertEqual(self.network.findrooturl(target), None)

    def test_findrooturl_found(self):
        target = self.tempdir()
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        rootfile = join(zdir, "Root")
        f = open(rootfile, "w")
        f.write(sample_rooturl + "\n")
        f.close()
        self.assertEqual(self.network.findrooturl(target), sample_rooturl)

    def test_saverooturl(self):
        self.network.setrooturl(sample_rooturl)
        target = self.tempdir()
        zdir = join(target, "@@Zope")
        os.mkdir(zdir)
        rootfile = join(zdir, "Root")
        self.network.saverooturl(target)
        f = open(rootfile, "r")
        data = f.read()
        f.close()
        self.assertEqual(data.strip(), sample_rooturl)

    def test_loadrooturl(self):
        target = self.tempdir()
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
