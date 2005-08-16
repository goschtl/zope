##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Tests for the Committer class.

$Id$
"""
import os
import shutil
import tempfile
import unittest

from zope.app import zapi
from zope.app.testing import ztapi
from zope.app.traversing.interfaces import TraversalError
from zope.interface import implements

from zope.xmlpickle import loads, dumps
from zope.fssync import fsutil
from zope.fssync.server.entryadapter import DefaultFileAdpater
from zope.fssync.tests.mockmetadata import MockMetadata
from zope.fssync.tests.tempfiles import TempFiles

from zope.fssync.server.entryadapter import DirectoryAdapter
from zope.app.container.interfaces import IContainer
from zope.app.filerepresentation.interfaces import IFileFactory
from zope.app.filerepresentation.interfaces import IDirectoryFactory
from zope.app.traversing.interfaces import IContainmentRoot
from zope.app.traversing.interfaces import ITraversable, ITraverser
from zope.app.location import Location
from zope.app.testing.placelesssetup import PlacelessSetup

from zope.app.fssync import committer, syncer # The module
from zope.app.fssync.committer import Checker, Committer, SynchronizationError
from zope.app.fssync.fsregistry import provideSynchronizer, fsRegistry
from zope.app.fssync.interfaces import IGlobalFSSyncUtility


class Sample(object):
    pass


class PretendContainer(Location):

    implements(IContainer, ITraversable, ITraverser)

    def __init__(self):
        self.holding = {}

    def __setitem__(self, name, value):
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

    def get(self, name):
        name = name.lower()
        return self.holding.get(name)

    def __contains__(self, name):
        name = name.lower()
        return name in self.holding

    def keys(self):
        return self.holding.keys()

    def items(self):
        return self.holding.items()

    def traverse(self, name, furtherPath):
        try:
            return self[name]
        except KeyError:
            raise TraversalError

PCname = PretendContainer.__module__ + "." + PretendContainer.__name__

class PretendRootContainer(PretendContainer):

    implements(IContainmentRoot)


class DictAdapter(DefaultFileAdpater):

    def setBody(self, body):
        old = self.context
        if old.__class__ is not dict:
            raise AssertionError("old.__class__ is not dict")
        new = loads(body)
        if type(new) is not dict:
            raise AssertionError("type(new) is not dict")
        old.update(new)
        for key in old.keys():
            if key not in new:
                del old[key]


class TestBase(PlacelessSetup, TempFiles):

    # Base class for test classes

    def setUp(self):
        super(TestBase, self).setUp()

        # Set up FSRegistryUtility
        gsm = zapi.getGlobalSiteManager()
        gsm.provideUtility(IGlobalFSSyncUtility, fsRegistry)
        provideSynchronizer(None, DefaultFileAdpater)

        # Set up temporary name administration
        TempFiles.setUp(self)

    def tearDown(self):
        # Clean up temporary files and directories
        TempFiles.tearDown(self)

        PlacelessSetup.tearDown(self)


def file_factory_maker(container):
    def file_factory(name, content_type, data):
        return loads(data)
    return file_factory

def directory_factory_maker(container):
    def directory_factory(name):
        return PretendContainer()
    return directory_factory

def sort(lst):
    lst.sort()
    return lst


class TestSyncerModule(TestBase):

    def setUp(self):
        super(TestSyncerModule, self).setUp()
        self.location = tempfile.mktemp()
        os.mkdir(self.location)

    def tearDown(self):
        super(TestSyncerModule, self).tearDown()
        shutil.rmtree(self.location)

    def test_toFS(self):
        obj = Sample()
        syncer.toFS(obj, "foo", self.location)

    def test_getSerializer(self):
        obj = Sample()
        adapter = syncer.getSerializer(obj)
        self.assertEqual(adapter.__class__, DefaultFileAdpater)

class TestCommitterModule(TestBase):

    def test_read_file(self):
        data = "12345\rabcde\n12345\r\nabcde"
        tfn = self.tempfile(data, "wb")
        x = committer.read_file(tfn)
        self.assertEqual(x, data)

    def test_set_item_non_icontainer(self):
        container = {}
        committer.set_item(container, "foo", 42)
        self.assertEqual(container, {"foo": 42})

    def test_set_item_icontainer_new(self):
        container = PretendContainer()
        committer.set_item(container, "foo", 42)
        self.assertEqual(container.holding, {"foo": 42})

    def test_set_item_icontainer_replace(self):
        container = PretendContainer()
        committer.set_item(container, "foo", 42)
        committer.set_item(container, "foo", 24, replace=True)
        self.assertEqual(container.holding, {"foo": 24})

    def test_set_item_icontainer_error_nonexisting(self):
        container = PretendContainer()
        self.assertRaises(KeyError, committer.set_item,
                          container, "foo", 42, replace=True)

    def create_object(self, *args, **kw):
        # Helper for the create_object() tests.
        c = Committer(syncer.getSerializer,
                      getAnnotations=syncer.getAnnotations)
        c.create_object(*args, **kw)

    def test_create_object_extra(self):
        class TestContainer(object):
            # simulate AttrMapping
            def __setitem__(self, name, value):
                self.name = name
                self.value = value
        class TestRoot(object):
            implements(IContainmentRoot, ITraverser)
            def traverse(self, *args):
                pass
        fspath = tempfile.mktemp()
        f = open(fspath, 'w')
        f.write('<pickle> <string>text/plain</string> </pickle>')
        f.close()
        container = TestContainer()
        name = "contentType"
        root = TestRoot()
        try:
            self.create_object(container, name, {}, fspath, context=root)
        finally:
            os.remove(fspath)
        self.assertEqual(container.name, name)
        self.assertEqual(container.value, "text/plain")

    def test_create_object_factory_file(self):
        provideSynchronizer(dict, DictAdapter)
        container = {}
        entry = {"flag": "added", "factory": "__builtin__.dict"}
        tfn = os.path.join(self.tempdir(), "foo")
        data = {"hello": "world"}
        self.writefile(dumps(data), tfn)
        self.create_object(container, "foo", entry, tfn)
        self.assertEqual(container, {"foo": data})

    def test_create_object_factory_directory(self):
        provideSynchronizer(PretendContainer, DirectoryAdapter)
        container = {}
        entry = {"flag": "added", "factory": PCname}
        tfn = os.path.join(self.tempdir(), "foo")
        os.mkdir(tfn)
        self.create_object(container, "foo", entry, tfn)
        self.assertEqual(container.keys(), ["foo"])
        self.assertEqual(container["foo"].__class__, PretendContainer)

    def test_create_object_default(self):
        container = PretendRootContainer()
        entry = {"flag": "added"}
        data = ["hello", "world"]
        tfn = os.path.join(self.tempdir(), "foo")
        self.writefile(dumps(data), tfn, "wb")
        self.create_object(container, "foo", entry, tfn)
        self.assertEqual(container.items(), [("foo", ["hello", "world"])])

    def test_create_object_ifilefactory(self):
        ztapi.provideAdapter(IContainer, IFileFactory, file_factory_maker)
        container = PretendContainer()
        entry = {"flag": "added"}
        data = ["hello", "world"]
        tfn = os.path.join(self.tempdir(), "foo")
        self.writefile(dumps(data), tfn, "wb")
        self.create_object(container, "foo", entry, tfn)
        self.assertEqual(container.holding, {"foo": ["hello", "world"]})

    def test_create_object_idirectoryfactory(self):
        ztapi.provideAdapter(IContainer, IDirectoryFactory,
                             directory_factory_maker)
        container = PretendContainer()
        entry = {"flag": "added"}
        tfn = os.path.join(self.tempdir(), "foo")
        os.mkdir(tfn)
        self.create_object(container, "foo", entry, tfn)
        self.assertEqual(container.holding["foo"].__class__, PretendContainer)


class TestCheckerClass(TestBase):

    def setUp(self):
        # Set up base class (PlacelessSetup and TempNames)
        TestBase.setUp(self)

        # Set up environment
        provideSynchronizer(PretendContainer, DirectoryAdapter)
        provideSynchronizer(dict, DictAdapter)
        ztapi.provideAdapter(IContainer, IFileFactory, file_factory_maker)
        ztapi.provideAdapter(IContainer, IDirectoryFactory,
                             directory_factory_maker)

        # Set up fixed part of object tree
        self.parent = PretendContainer()
        self.child = PretendContainer()
        self.grandchild = PretendContainer()
        self.parent["child"] = self.child
        self.child["grandchild"] = self.grandchild
        self.foo = ["hello", "world"]
        self.child["foo"] = self.foo

        # Set up fixed part of filesystem tree
        self.parentdir = self.tempdir()
        self.childdir = os.path.join(self.parentdir, "child")
        os.mkdir(self.childdir)
        self.foofile = os.path.join(self.childdir, "foo")
        self.writefile(dumps(self.foo), self.foofile, "wb")
        self.originalfoofile = fsutil.getoriginal(self.foofile)
        self.writefile(dumps(self.foo), self.originalfoofile, "wb")
        self.grandchilddir = os.path.join(self.childdir, "grandchild")
        os.mkdir(self.grandchilddir)

        # Set up metadata
        self.metadata = MockMetadata()
        self.getentry = self.metadata.getentry

        # Set up fixed part of entries
        self.parententry = self.getentry(self.parentdir)
        self.parententry["path"] = "/parent"
        self.childentry = self.getentry(self.childdir)
        self.childentry["path"] = "/parent/child"
        self.grandchildentry = self.getentry(self.grandchilddir)
        self.grandchildentry["path"] = "/parent/child/grandchild"
        self.fooentry = self.getentry(self.foofile)
        self.fooentry["path"] = "/parent/child/foo"

        # Set up checker
        self.checker = Checker(syncer.getSerializer, self.metadata,
                               getAnnotations=syncer.getAnnotations)

    def check_errors(self, expected_errors):
        # Helper to call the checker and assert a given set of errors
        self.checker.check(self.parent, "", self.parentdir)
        self.assertEqual(sort(self.checker.errors()), sort(expected_errors))

    def check_no_errors(self):
        # Helper to call the checker and assert there are no errors
        self.check_errors([])

    def test_vanilla(self):
        # The vanilla situation should not be an error
        self.check_no_errors()

    def test_file_changed(self):
        # Changing a file is okay
        self.newfoo = self.foo + ["news"]
        self.writefile(dumps(self.newfoo), self.foofile, "wb")
        self.check_no_errors()

    def test_file_type_changed(self):
        # Changing a file's type is okay
        self.newfoo = ("one", "two")
        self.fooentry["type"] = "__builtin__.tuple"
        self.writefile(dumps(self.newfoo), self.foofile, "wb")
        self.check_no_errors()

    def test_file_conflict(self):
        # A real conflict is an error
        newfoo = self.foo + ["news"]
        self.writefile(dumps(newfoo), self.foofile, "wb")
        self.foo.append("something else")
        self.check_errors([self.foofile])

    def test_file_sticky_conflict(self):
        # A sticky conflict is an error
        self.fooentry["conflict"] = 1
        self.check_errors([self.foofile])

    def test_file_added(self):
        # Adding a file properly is okay
        self.bar = ["this", "is", "bar"]
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(self.bar), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["flag"] = "added"
        self.check_no_errors()

    def test_file_added_no_file(self):
        # Flagging a non-existing file as added is an error
        barfile = os.path.join(self.childdir, "bar")
        barentry = self.getentry(barfile)
        barentry["flag"] = "added"
        self.check_errors([barfile])

    def test_file_spurious(self):
        # A spurious file (empty entry) is okay
        bar = ["this", "is", "bar"]
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(bar), barfile, "wb")
        self.check_no_errors()

    def test_file_added_no_flag(self):
        # Adding a file without setting the "added" flag is an error
        bar = ["this", "is", "bar"]
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(bar), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["path"] = "/parent/child/bar"
        self.check_errors([barfile])

    def test_file_added_twice(self):
        # Adding a file in both places is an error
        bar = ["this", "is", "bar"]
        self.child["bar"] = bar
        barfile = os.path.join(self.childdir, "bar")
        self.writefile(dumps(bar), barfile, "wb")
        barentry = self.getentry(barfile)
        barentry["path"] = "/parent/child/bar"
        self.check_errors([barfile])

    def test_file_lost(self):
        # Losing a file is an error
        os.remove(self.foofile)
        self.check_errors([self.foofile])

    def test_file_lost_originial(self):
        # Losing the original file is an error
        os.remove(self.originalfoofile)
        self.check_errors([self.foofile])

    def test_file_removed(self):
        # Removing a file properly is okay
        os.remove(self.foofile)
        self.fooentry["flag"] = "removed"
        self.check_no_errors()

    def test_file_removed_conflict(self):
        # Removing a file that was changed in the database is an error
        os.remove(self.foofile)
        self.fooentry["flag"] = "removed"
        self.foo.append("news")
        self.check_errors([self.foofile])

    def test_file_removed_twice(self):
        # Removing a file in both places is an error
        os.remove(self.foofile)
        self.fooentry["flag"] = "removed"
        del self.child["foo"]
        self.check_errors([self.foofile])

    def test_file_removed_object(self):
        # Removing the object should cause a conflict
        del self.child["foo"]
        self.check_errors([self.foofile])

    def test_file_entry_cleared(self):
        # Clearing out a file's entry is an error
        self.fooentry.clear()
        self.check_errors([self.foofile])

    def test_dir_added(self):
        # Adding a directory is okay
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["flag"] = "added"
        self.check_no_errors()

    def test_dir_spurious(self):
        # A spurious directory is okay
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        self.check_no_errors()

    def test_dir_added_no_flag(self):
        # Adding a directory without setting the "added" flag is an error
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["path"] = "/parent/child/bar"
        self.check_errors([bardir])

    def test_dir_lost(self):
        # Losing a directory is an error
        shutil.rmtree(self.grandchilddir)
        self.check_errors([self.grandchilddir])

    def test_dir_removed(self):
        # Removing a directory properly is okay
        shutil.rmtree(self.grandchilddir)
        self.grandchildentry["flag"] = "removed"
        self.check_no_errors()

    def test_dir_entry_cleared(self):
        # Clearing ot a directory's entry is an error
        self.grandchildentry.clear()
        self.check_errors([self.grandchilddir])

    def test_tree_added(self):
        # Adding a subtree is okay
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["path"] = "/parent/child/bar"
        barentry["flag"] = "added"
        bazfile = os.path.join(bardir, "baz")
        self.baz = ["baz"]
        self.writefile(dumps(self.baz), bazfile, "wb")
        bazentry = self.getentry(bazfile)
        bazentry["flag"] = "added"
        burpdir = os.path.join(bardir, "burp")
        os.mkdir(burpdir)
        burpentry = self.getentry(burpdir)
        burpentry["flag"] = "added"
        self.check_no_errors()

    def test_tree_added_no_flag(self):
        # Adding a subtree without flagging everything as added is an error
        bardir = os.path.join(self.childdir, "bar")
        os.mkdir(bardir)
        barentry = self.getentry(bardir)
        barentry["path"] = "/parent/child/bar"
        barentry["flag"] = "added"
        bazfile = os.path.join(bardir, "baz")
        baz = ["baz"]
        self.writefile(dumps(baz), bazfile, "wb")
        bazentry = self.getentry(bazfile)
        bazentry["path"] = "/parent/child/bar/baz"
        burpdir = os.path.join(bardir, "burp")
        os.mkdir(burpdir)
        burpentry = self.getentry(burpdir)
        burpentry["path"] = "/parent/child/bar/burp"
        self.check_errors([bazfile, burpdir])

    def test_tree_removed(self):
        # Removing a subtree is okay
        shutil.rmtree(self.childdir)
        self.childentry["flag"] = "removed"
        self.grandchildentry.clear()
        self.fooentry.clear()
        self.check_no_errors()

    # XXX Extra and Annotations is not tested directly

    # XXX Changing directories into files or vice versa is not tested



class TestCommitterClass(TestCheckerClass):

    # This class extends all tests from TestCheckerClass that call
    # self.check_no_errors() to carry out the change and check on it.
    # Yes, this means that all the tests that call check_errors() are
    # repeated.  Big deal. :-)

    def __init__(self, name):
        TestCheckerClass.__init__(self, name)
        self.name = name

    def setUp(self):
        TestCheckerClass.setUp(self)
        self.committer = Committer(syncer.getSerializer, self.metadata,
                                   getAnnotations=syncer.getAnnotations)

    def check_no_errors(self):
        TestCheckerClass.check_no_errors(self)
        self.committer.synch(self.parent, "", self.parentdir)
        name = "verify" + self.name[4:]
        method = getattr(self, name, None)
        if method:
            method()
        else:
            print "?", name

    def verify_vanilla(self):
        self.assertEqual(self.parent.keys(), ["child"])
        self.assertEqual(self.parent["child"], self.child)
        self.assertEqual(sort(self.child.keys()), ["foo", "grandchild"])
        self.assertEqual(self.child["foo"], self.foo)
        self.assertEqual(self.child["grandchild"], self.grandchild)
        self.assertEqual(self.grandchild.keys(), [])

    def verify_file_added(self):
        self.assertEqual(self.child["bar"], self.bar)
        self.assertEqual(sort(self.child.keys()), ["bar", "foo", "grandchild"])

    def verify_file_changed(self):
        self.assertEqual(self.child["foo"], self.newfoo)
    
    def verify_file_removed(self):
        self.assertEqual(self.child.keys(), ["grandchild"])

    def verify_file_spurious(self):
        self.verify_vanilla()

    def verify_file_type_changed(self):
        self.assertEqual(self.child["foo"], self.newfoo)

    def verify_dir_removed(self):
        self.assertEqual(self.child.keys(), ["foo"])

    def verify_dir_added(self):
        self.assertEqual(sort(self.child.keys()), ["bar", "foo", "grandchild"])

    def verify_dir_spurious(self):
        self.verify_vanilla()

    def verify_tree_added(self):
        self.assertEqual(sort(self.child.keys()), ["bar", "foo", "grandchild"])
        bar = self.child["bar"]
        self.assertEqual(bar.__class__, PretendContainer)
        baz = bar["baz"]
        self.assertEqual(self.baz, baz)

    def verify_tree_removed(self):
        self.assertEqual(self.parent.keys(), [])


def test_suite():
    s = unittest.TestSuite()
    s.addTest(unittest.makeSuite(TestSyncerModule))
    s.addTest(unittest.makeSuite(TestCommitterModule))
    s.addTest(unittest.makeSuite(TestCheckerClass))
    s.addTest(unittest.makeSuite(TestCommitterClass))
    return s

def test_main():
    unittest.TextTestRunner().run(test_suite())

if __name__=='__main__':
    test_main()
