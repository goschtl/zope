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

$Id: test_metadata.py,v 1.5 2003/07/25 19:34:51 fdrake Exp $
"""

import os
import unittest

from os.path import dirname, isfile, join

from zope.xmlpickle import loads

from zope.fssync.metadata import Metadata
from zope.fssync.tests.tempfiles import TempFiles

class TestMetadata(TempFiles):

    def test_initial_state(self):
        md = Metadata()
        dir = self.tempdir()
        self.assertEqual(md.getnames(dir), [])
        foo = join(dir, "foo")
        self.assertEqual(md.getentry(foo), {})
        self.assertEqual(md.getnames(dir), [])

    def test_adding(self):
        md = Metadata()
        dir = self.tempdir()
        foo = join(dir, "foo")
        e = md.getentry(foo)
        e["hello"] = "world"
        self.assertEqual(md.getentry(foo), {"hello": "world"})
        self.assert_(md.getentry(foo) is e)
        self.assertEqual(md.getnames(dir), ["foo"])
        return md, foo

    def test_deleting(self):
        md, foo = self.test_adding()
        dir = dirname(foo)
        md.getentry(foo).clear()
        self.assertEqual(md.getentry(foo), {})
        self.assertEqual(md.getnames(dir), [])

    def test_flush(self):
        md, foo = self.test_adding()
        dir = dirname(foo)
        md.flush()
        efile = join(dir, "@@Zope", "Entries.xml")
        self.assert_(isfile(efile))
        data = self.readfile(efile)
        entries = loads(data)
        self.assertEqual(entries, {"foo": {"hello": "world"}})
        md.getentry(foo).clear()
        md.flush()
        self.assert_(isfile(efile))
        data = self.readfile(efile)
        entries = loads(data)
        self.assertEqual(entries, {})

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(TestMetadata)

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
