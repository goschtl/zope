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
"""Tests for the functions in the fsutil module.

$Id: test_fsutil.py,v 1.1 2003/05/14 22:16:09 gvanrossum Exp $
"""

import os
import tempfile
import unittest

from os.path import split, join, exists, isdir, isfile

from zope.fssync import fsutil

class TestFSUtil(unittest.TestCase):

    def test_split(self):
        self.assertEqual(fsutil.split(join("foo", "bar")), ("foo", "bar"))
        self.assertEqual(fsutil.split("foo"), (os.curdir, "foo"))
        self.assertEqual(fsutil.split(join("foo", "")), (os.curdir, "foo"))
        self.assertEqual(fsutil.split(join("foo", os.curdir)),
                         (os.curdir, "foo"))
        self.assertEqual(fsutil.split(join("foo", "bar", os.pardir)),
                         (os.curdir, "foo"))
        self.assertEqual(fsutil.split(os.curdir), split(os.getcwd()))

    def test_getspecial(self):
        self.assertEqual(fsutil.getspecial("foo/bar", "X"), "foo/@@Zope/X/bar")

    def test_getoriginal(self):
        self.assertEqual(fsutil.getoriginal("foo/bar"),
                         "foo/@@Zope/Original/bar")

    def test_getextra(self):
        self.assertEqual(fsutil.getextra("foo/bar"), "foo/@@Zope/Extra/bar")

    def test_getannotations(self):
        self.assertEqual(fsutil.getannotations("foo/bar"),
                         "foo/@@Zope/Annotations/bar")

    def test_ensuredir(self):
        tmpdir = tempfile.mktemp()
        try:
            self.assertEqual(exists(tmpdir), False)
            self.assertEqual(isdir(tmpdir), False)
            fsutil.ensuredir(tmpdir)
            self.assertEqual(isdir(tmpdir), True)
            fsutil.ensuredir(tmpdir)
            self.assertEqual(isdir(tmpdir), True)
        finally:
            if isdir(tmpdir):
                os.rmdir(tmpdir)

    def test_ensuredir_error(self):
        tmpfile = tempfile.mktemp()
        try:
            f = open(tmpfile, "w")
            try:
                f.write("x\n")
            finally:
                f.close()
            self.assertRaises(OSError, fsutil.ensuredir, tmpfile)
        finally:
            if isfile(tmpfile):
                os.remove(tmpfile)

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestFSUtil)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
