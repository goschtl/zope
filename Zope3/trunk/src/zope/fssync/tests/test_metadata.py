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
"""Tests for the Metadata class.

$Id: test_metadata.py,v 1.2 2003/05/12 20:41:23 gvanrossum Exp $
"""

import os
import shutil
import unittest
import tempfile

from os.path import exists, isdir, isfile, split, join, realpath, normcase

from zope.xmlpickle import loads, dumps

from zope.fssync.metadata import Metadata

class TestMetadata(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)
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
        # Register and create a temporary directory
        dir = tempfile.mktemp()
        self.tempfiles.append(dir)
        os.mkdir(dir)
        return dir

    def test_initial_state(self):
        md = Metadata()
        dir = self.adddir()
        self.assertEqual(md.getnames(dir), [])
        foo = join(dir, "foo")
        self.assertEqual(md.getentry(foo), {})
        self.assertEqual(md.getnames(dir), [])

    def test_adding(self):
        md = Metadata()
        dir = self.adddir()
        foo = join(dir, "foo")
        e = md.getentry(foo)
        e["hello"] = "world"
        self.assertEqual(md.getentry(foo), {"hello": "world"})
        self.assert_(md.getentry(foo) is e)
        self.assertEqual(md.getnames(dir), ["foo"])
        return md, foo

    def test_deleting(self):
        md, foo = self.test_adding()
        dir = os.path.dirname(foo)
        md.getentry(foo).clear()
        self.assertEqual(md.getentry(foo), {})
        self.assertEqual(md.getnames(dir), [])

    def test_flush(self):
        md, foo = self.test_adding()
        dir = os.path.dirname(foo)
        md.flush()
        efile = join(dir, "@@Zope", "Entries.xml")
        self.assert_(isfile(efile))
        f = open(efile)
        data = f.read()
        f.close()
        entries = loads(data)
        self.assertEqual(entries, {"foo": {"hello": "world"}})
        md.getentry(foo).clear()
        md.flush()
        self.assert_(not exists(efile))

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestMetadata)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
