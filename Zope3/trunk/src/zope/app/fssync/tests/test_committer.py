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
"""Tests for the Committer class.

$Id: test_committer.py,v 1.3 2003/05/28 14:49:08 gvanrossum Exp $
"""

import os
import shutil
import unittest

from zope.component.service import serviceManager
from zope.component.adapter import provideAdapter
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.testing.cleanup import CleanUp

from zope.xmlpickle import loads, dumps
from zope.fssync import fsutil
from zope.fssync.tests.mockmetadata import MockMetadata
from zope.fssync.tests.tempfiles import TempFiles

from zope.app.interfaces.container import IContainer
from zope.app.interfaces.file import IFileFactory
from zope.app.interfaces.fssync import IGlobalFSSyncService

from zope.app.fssync.committer import Committer, SynchronizationError
from zope.app.fssync.fsregistry import provideSynchronizer, fsRegistry
from zope.app.fssync.classes import Default

from zope.app.content.fssync import DirectoryAdapter

class Sample(object):
    pass

class PretendContainer(object):
    
    __implements__ = IContainer

    def __init__(self):
        self.holding = {}

    def setObject(self, name, value):
        name = name.lower()
        if name in self.holding:
            raise KeyError
        self.holding[name] = value
        return name

    def __delitem__(self, name):
        name = name.lower()
        del self.holding[name]

    def __getitem__(self, name):
        name = name.lower()
        return self.holding[name]

    def __contains__(self, name):
        name = name.lower()
        return name in self.holding

    def items(self):
        return self.holding.items()

PCname = PretendContainer.__module__ + "." + PretendContainer.__name__

class DictAdapter(Default):

    def setBody(self, body):
        old = self.context
        assert type(old) is dict
        new = loads(body)
        assert type(new) is dict
        old.update(new)
        for key in old.keys():
            if key not in new:
                del old[key]

class TestCommitter(TempFiles, PlacelessSetup):

    def setUp(self):
        # Set up standard services
        PlacelessSetup.setUp(self)

        # Set up FSRegistryService
        serviceManager.defineService("FSRegistryService", IGlobalFSSyncService)
        serviceManager.provideService("FSRegistryService", fsRegistry)
        provideSynchronizer(None, Default)

        # Set up temporary name administration
        TempFiles.setUp(self)

        # Instance initialization
        self.metadata = MockMetadata() 
        self.com = Committer(self.metadata)
        self.getentry = self.metadata.getentry
        self.getnames = self.metadata.getnames

    def tearDown(self):
        # Clean up temporary files and directories
        TempFiles.tearDown(self)

        # Clean up service registrations etc.
        PlacelessSetup.tearDown(self)

    def test_get_adapter(self):
        obj = Sample()
        adapter = self.com.get_adapter(obj)
        self.assertEqual(adapter.__class__, Default)

    def test_remove(self):
        tfn = self.tempfile("12345")
        self.com.remove(tfn)
        self.failIf(os.path.exists(tfn))
        self.com.remove(tfn)
        tfn = self.tempdir()
        self.writefile("12345", os.path.join(tfn, "foo", "bar"))
        self.com.remove(tfn)
        self.failIf(os.path.exists(tfn))

    def test_remove_all(self):
        tfn = self.tempdir()
        foo = os.path.join(tfn, "foo")
        originalfoo = fsutil.getoriginal(foo)
        extrafoo = os.path.join(fsutil.getextra(foo), "x")
        annfoo = os.path.join(fsutil.getannotations(foo), "a")
        self.writefile("12345", foo)
        self.writefile("12345", originalfoo)
        self.writefile("12345", extrafoo)
        self.writefile("12345", annfoo)
        self.com.remove_all(foo)
        self.failIf(os.path.exists(foo))
        self.failIf(os.path.exists(originalfoo))
        self.failIf(os.path.exists(extrafoo))
        self.failIf(os.path.exists(annfoo))

    def test_write_file(self):
        data = "12345\rabcde\n12345\r\nabcde"
        tfn = self.tempfile(None)
        self.com.write_file(data, tfn)
        f = open(tfn, "rb")
        try:
            x = f.read()
        finally:
            f.close()
        self.assertEqual(x, data)

    def test_write_file_and_original(self):
        data = "12345\rabcde\n12345\r\nabcde"
        tfn = self.tempdir()
        foofile = os.path.join(tfn, "foo")
        self.com.write_file_and_original(data, foofile)
        f = open(foofile, "rb")
        try:
            x = f.read()
        finally:
            f.close()
        self.assertEqual(x, data)
        f = open(fsutil.getoriginal(foofile), "rb")
        try:
            x = f.read()
        finally:
            f.close()
        self.assertEqual(x, data)

    def test_read_file(self):
        data = "12345\rabcde\n12345\r\nabcde"
        tfn = self.tempfile(data)
        x = self.com.read_file(tfn)
        self.assertEqual(x, data)

    def test_load_file(self):
        data = {"foo": [42]}
        tfn = self.tempfile(dumps(data))
        x = self.com.load_file(tfn)
        self.assertEqual(x, data)

    def test_set_item_non_icontainer(self):
        container = {}
        self.com.set_item(container, "foo", 42)
        self.assertEqual(container, {"foo": 42})

    def test_set_item_icontainer_new(self):
        container = PretendContainer()
        self.com.set_item(container, "foo", 42)
        self.assertEqual(container.holding, {"foo": 42})

    def test_set_item_icontainer_replace(self):
        container = PretendContainer()
        self.com.set_item(container, "foo", 42)
        self.com.set_item(container, "foo", 24, replace=True)
        self.assertEqual(container.holding, {"foo": 24})

    def test_set_item_icontainer_error_existing(self):
        container = PretendContainer()
        self.com.set_item(container, "foo", 42)
        self.assertRaises(KeyError, self.com.set_item,
                          container, "foo", 42)

    def test_set_item_icontainer_error_nonexisting(self):
        container = PretendContainer()
        self.assertRaises(KeyError, self.com.set_item,
                          container, "foo", 42, replace=True)

    def test_set_item_icontainer_error_newname(self):
        container = PretendContainer()
        self.assertRaises(SynchronizationError, self.com.set_item,
                          container, "Foo", 42)

    def test_create_object_factory(self):
        container = {}
        entry = {"flag": "added", "factory": "__builtin__.int"}
        tfn = os.path.join(self.tempdir(), "foo")
        self.com.create_object(container, "foo", entry, tfn)
        self.assertEqual(container, {"foo": 0})
        self.assertEqual(entry, {"factory": None, "type": "__builtin__.int"})

    def test_create_object_default(self):
        container = {}
        entry = {"flag": "added"}
        data = ["hello", "world"]
        tfn = os.path.join(self.tempdir(), "foo")
        self.writefile(dumps(data), tfn)
        self.com.create_object(container, "foo", entry, tfn)
        self.assertEqual(container, {"foo": ["hello", "world"]})
        self.assertEqual(entry, {"factory": None, "type": "__builtin__.list"})

    def test_create_object_ifilefactory(self):
        def factory_maker(container):
            def factory(name, content_type, data):
                return loads(data)
            return factory
        provideAdapter(IContainer, IFileFactory, factory_maker)
        container = PretendContainer()
        entry = {"flag": "added"}
        data = ["hello", "world"]
        tfn = os.path.join(self.tempdir(), "foo")
        self.writefile(dumps(data), tfn)
        self.com.create_object(container, "foo", entry, tfn)
        self.assertEqual(container.holding, {"foo": ["hello", "world"]})
        self.assertEqual(entry, {"factory": None, "type": "__builtin__.list"})

    def test_synch(self):
        # This is a big-ass test that tests various aspects of
        # synch(), including synch_dir(), synch_new(), and
        # synch_old().  It's such a pain to set things up that I don't
        # split it up in a separate test method for each case in each
        # method.  Nevertheless I expect to get good coverage.

        provideSynchronizer(PretendContainer, DirectoryAdapter)
        provideSynchronizer(dict, DictAdapter)
        parent = PretendContainer()
        child = PretendContainer()
        parent.setObject("child", child)
        foo = {}
        child.setObject("foo", foo)
        parentdir = self.tempdir()
        childdir = os.path.join(parentdir, "child")
        foofile = os.path.join(childdir, "foo")
        self.writefile(dumps(foo), foofile)
        originalfoofile = fsutil.getoriginal(foofile)
        self.writefile(dumps(foo), originalfoofile)
        parententry = self.getentry(parentdir)
        parententry["@"] = "@" # To make it non-empty
        childentry = self.getentry(childdir)
        childentry["@"] = "@"
        fooentry = self.getentry(foofile)
        fooentry["type"] = "__builtin__.dict"

        # Test a no-op
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [])
        self.assertEqual(parent.holding, {"child": child})
        self.assertEqual(child.holding, {"foo": foo})
        self.assertEqual(self.com.read_file(foofile), dumps(foo))
        self.assertEqual(self.com.read_file(originalfoofile), dumps(foo))

        # Test modifying a file
        newfoo = {"x": 42}
        self.writefile(dumps(newfoo), foofile)
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [])
        self.assertEqual(parent.holding, {"child": child})
        self.assertEqual(child.holding, {"foo": newfoo})
        self.assertEqual(self.com.read_file(foofile), dumps(newfoo))
        self.assertEqual(self.com.read_file(originalfoofile), dumps(newfoo))

        # Test adding a file
        bar = {"y": 42}
        barfile = os.path.join(childdir, "bar")
        originalbarfile = fsutil.getoriginal(barfile)
        barentry = self.getentry(barfile)
        barentry["flag"] = "added"
        self.writefile(dumps(bar), barfile)
        self.com.synch(parent, "", parentdir)
        self.assertEqual(child.holding, {"foo": newfoo, "bar": bar})
        self.assertEqual(self.com.read_file(barfile), dumps(bar))
        self.assertEqual(self.com.read_file(originalbarfile), dumps(bar))
        self.assertEqual(barentry.get("flag"), None)

        # Test removing a file
        os.remove(barfile)
        barentry["flag"] = "removed"
        self.com.synch(parent, "", parentdir)
        self.assertEqual(child.holding, {"foo": newfoo})
        self.assertEqual(barentry, {})
        self.failIf(os.path.exists(barfile))
        self.failIf(os.path.exists(originalbarfile))

        # Test changing the type of an object
        altfoo = 42
        self.writefile(dumps(altfoo), foofile)
        fooentry["type"] = "__builtin__.int"
        self.com.synch(parent, "", parentdir)
        self.assertEqual(child.holding, {"foo": altfoo})
        self.assertEqual(self.com.read_file(foofile), dumps(altfoo))
        self.assertEqual(self.com.read_file(originalfoofile), dumps(altfoo))

        # Test adding an empty directory
        kwikdir = os.path.join(childdir, "kwik")
        os.mkdir(kwikdir)
        kwikentry = self.getentry(kwikdir)
        kwikentry["factory"] = PCname
        kwikentry["flag"] = "added"
        self.com.synch(parent, "", parentdir)
        self.failUnless("kwik" in child)
        self.assertEqual(child["kwik"].__class__, PretendContainer)
        self.assertEqual(kwikentry.get("flag"), None)

        # Test removing an empty directory
        kwikentry["flag"] = "removed"
        shutil.rmtree(kwikdir)
        self.com.synch(parent, "", parentdir)
        self.failIf("kwik" in child)
        self.assertEqual(kwikentry, {})

        # Test adding a non-empty directory tree (parent/child/kwik/kwek/kwak)
        kwikentry["flag"] = "added"
        kwikentry["factory"] = PCname
        kwekdir = os.path.join(kwikdir, "kwek")
        kwekentry = self.getentry(kwekdir)
        kwekentry["flag"] = "added"
        kwekentry["factory"] = PCname
        kwakfile = os.path.join(kwekdir, "kwak")
        kwakentry = self.getentry(kwakfile)
        kwakentry["flag"] = "added"
        data = dumps(["Google", "Kwik", "Kwek", "Kwak"])
        self.writefile(data, kwakfile)
        assert os.path.isdir(kwikdir)
        assert os.path.isdir(kwekdir)
        assert os.path.isfile(kwakfile)
        self.com.synch(parent, "", parentdir)
        self.assertEqual(kwikentry.get("flag"), None)
        self.assertEqual(kwekentry.get("flag"), None)
        self.assertEqual(kwakentry.get("flag"), None)
        self.failUnless(os.path.isfile(kwakfile))
        self.assertEqual(self.com.read_file(kwakfile), data)
        self.failUnless(os.path.isfile(fsutil.getoriginal(kwakfile)))

        # Test removing the subtree rooted at kwek
        kwekentry["flag"] = "removed"
        kwakentry["flag"] = "removed"
        os.remove(kwakfile)
        self.com.synch(parent, "", parentdir)
        self.assertEqual(kwekentry, {})
        self.assertEqual(kwakentry, {})
        self.failIf(os.path.exists(kwakfile))
        self.failIf(os.path.exists(kwekdir))
        self.failUnless(os.path.exists(kwikdir))

        # Test conflict reporting for object modified in both places
        self.writefile("something else", originalfoofile)
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [foofile])
        self.assertEqual(self.com.read_file(foofile),
                         self.com.read_file(originalfoofile))

        # Test conflict reporting for object added in both places
        os.remove(originalfoofile)
        fooentry["flag"] = "added"
        self.com.conflicts = []
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [foofile])
        self.assertEqual(fooentry.get("flag"), None)

        # Test conflict reporting for object removed from container
        del child["foo"]
        self.com.conflicts = []
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [foofile])

        # Test conflict reporting for existing file marked as removed
        fooentry["flag"] = "removed"
        self.com.conflicts = []
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [foofile])
        self.assertEqual(fooentry.get("flag"), None)

        # Test conflict reporting for non-existing file marked as added
        fooentry["flag"] = "added"
        self.com.conflicts = []
        self.com.synch(parent, "", parentdir)
        self.assertEqual(self.com.get_errors(), [foofile])
        self.assertEqual(fooentry.get("flag"), None)

        # XXX Manipulation of Extra and Annotations is not tested

        # XXX Changing directories into files or vice versa is not supported

def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestCommitter))
    return s

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
