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
"""Commit changes from the filesystem.

$Id: committer.py,v 1.8 2003/06/03 17:08:52 gvanrossum Exp $
"""

import os
import shutil

from zope.component import getAdapter, queryAdapter, getService
from zope.xmlpickle import dumps, loads
from zope.configuration.name import resolve
from zope.proxy import removeAllProxies

from zope.fssync.metadata import Metadata
from zope.fssync import fsutil

from zope.app.interfaces.fssync \
     import IObjectEntry, IObjectDirectory, IObjectFile

from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.container import IContainer, IZopeContainer
from zope.app.fssync.classes import Default
from zope.app.traversing import getPath, traverseName
from zope.app.interfaces.file import IFileFactory, IDirectoryFactory
from zope.app.event import publish
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.event.objectevent import ObjectModifiedEvent

class SynchronizationError(Exception):
    pass

class Checker(object):
    """Check that the filesystem is consistent with the object database.

    The public API consists of __init__(), check() and errors() only.
    """

    def __init__(self, metadata=None):
        """Constructor.  Optionally pass a metadata database."""
        if metadata is None:
            metadata = Metadata()
        self.metadata = metadata
        self.conflicts = []

    def errors(self):
        """Return a list of errors (conflicts).

        The return value is a list of filesystem pathnames for which
        a conflict exists.  A conflict usually refers to a file that
        was modified on the filesystem while the corresponding object
        was also modified in the database.  Other forms of conflicts
        are possible, e.g. a file added while an object was added in
        the corresponding place, or inconsistent labeling of the
        filesystem objects (e.g. an existing file marked as removed,
        or a non-existing file marked as added).
        """
        return self.conflicts

    def check(self, container, name, fspath):
        """Compare an object or object tree from the filesystem.

        If the originals on the filesystem are not uptodate, errors
        are reported by calling conflict().

        Invalid object names are reported by raising
        SynchronizationError.
        """

        if (os.sep in name or
            (os.altsep and os.altsep in name) or
            name == os.curdir or
            name == os.pardir or
            name == "." or
            name == ".." or
            "/" in name):
            # This name can't be mapped safely to the filesystem
            # or it is a magic value for traverseName (".", "..", "/")
            raise SynchronizationError("invalid separator in name %r" % name)

        if not name:
            self.check_dir(container, fspath)
        else:
            try:
                traverseName(container, name)
            except:
                self.check_new(fspath)
            else:
                self.check_old(container, name, fspath)

            # Now check extra and annotations
            try:
                obj = traverseName(container, name)
            except:
                pass
            else:
                adapter = get_adapter(obj)
                extra = adapter.extra()
                extrapath = fsutil.getextra(fspath)
                if extra is not None and os.path.exists(extrapath):
                    self.check_dir(extra, extrapath)
                ann = queryAdapter(obj, IAnnotations)
                annpath = fsutil.getannotations(fspath)
                if ann is not None and os.path.exists(annpath):
                    self.check_dir(ann, annpath)

    def check_dir(self, container, fspath):
        """Helper to check a directory."""
        adapter = get_adapter(container)
        nameset = {}
        if IObjectDirectory.isImplementedBy(adapter):
            for name, obj in adapter.contents():
                nameset[name] = 1
        else:
            for name in container:
                nameset[name] = 1
        for name in self.metadata.getnames(fspath):
            nameset[name] = 1
        # Sort the list of keys for repeatability
        names = nameset.keys()
        names.sort()
        for name in names:
            self.check(container, name, os.path.join(fspath, name))

    def check_new(self, fspath):
        """Helper to check a new object."""
        entry = self.metadata.getentry(fspath)
        if entry:
            if entry.get("flag") != "added":
                self.conflict(fspath)
            else:
                if not os.path.exists(fspath):
                    self.conflict(fspath)
            if os.path.isdir(fspath):
                # Recursively check registered contents
                for name in self.metadata.getnames(fspath):
                    self.check_new(os.path.join(fspath, name))

    def check_old(self, container, name, fspath):
        """Helper to check an existing object."""
        entry = self.metadata.getentry(fspath)
        if not entry:
            self.conflict(fspath)
        if "conflict" in entry:
            self.conflict(fspath)
        flag = entry.get("flag")
        if flag == "removed":
            if os.path.exists(fspath):
                self.conflict(fspath)
        else:
            if not os.path.exists(fspath):
                self.conflict(fspath)
        obj = traverseName(container, name)
        adapter = get_adapter(obj)
        if IObjectDirectory.isImplementedBy(adapter):
            if flag != "removed" or os.path.exists(fspath):
                self.check_dir(obj, fspath)
        else:
            if flag == "added":
                self.conflict(fspath)
            oldfspath = fsutil.getoriginal(fspath)
            if not os.path.exists(oldfspath):
                self.conflict(fspath)
            else:
                olddata = read_file(oldfspath)
                curdata = adapter.getBody()
                if curdata != olddata:
                    self.conflict(fspath)

    def conflict(self, fspath):
        """Helper to report a conflict.

        Conflicts can be retrieved by calling errors().
        """
        if fspath not in self.conflicts:
            self.conflicts.append(fspath)

class Committer(object):
    """Commit changes from the filesystem to the object database.

    The filesystem's originals must consistent with the object
    database; this should be checked beforehand by a Checker instance
    with the same arguments.

    The public API consists of __init__() and synch() only.
    """

    def __init__(self, metadata=None):
        """Constructor.  Optionally pass a metadata database."""
        if metadata is None:
            metadata = Metadata()
        self.metadata = metadata

    def synch(self, container, name, fspath):
        """Synchronize an object or object tree from the filesystem.

        SynchronizationError is raised for errors that can't be
        corrected by a update operation, including invalid object
        names.
        """

        if (os.sep in name or
            (os.altsep and os.altsep in name) or
            name == os.curdir or
            name == os.pardir or
            name == "." or
            name == ".." or
            "/" in name):
            # This name can't be mapped safely to the filesystem
            # or it is a magic value for traverseName (".", "..", "/")
            raise SynchronizationError("invalid separator in name %r" % name)

        if not name:
            self.synch_dir(container, fspath)
        else:
            try:
                traverseName(container, name)
            except:
                self.synch_new(container, name, fspath)
            else:
                self.synch_old(container, name, fspath)

            # Now update extra and annotations
            try:
                obj = traverseName(container, name)
            except:
                pass
            else:
                adapter = get_adapter(obj)
                extra = adapter.extra()
                extrapath = fsutil.getextra(fspath)
                if extra is not None and os.path.exists(extrapath):
                    self.synch_dir(extra, extrapath)
                ann = queryAdapter(obj, IAnnotations)
                annpath = fsutil.getannotations(fspath)
                if ann is not None and os.path.exists(annpath):
                    self.synch_dir(ann, annpath)

    def synch_dir(self, container, fspath):
        """Helper to synchronize a directory."""
        adapter = get_adapter(container)
        nameset = {}
        if IObjectDirectory.isImplementedBy(adapter):
            for name, obj in adapter.contents():
                nameset[name] = 1
        else:
            for name in container:
                nameset[name] = 1
        for name in self.metadata.getnames(fspath):
            nameset[name] = 1
        # Sort the list of keys for repeatability
        names = nameset.keys()
        names.sort()
        for name in names:
            self.synch(container, name, os.path.join(fspath, name))

    def synch_new(self, container, name, fspath):
        """Helper to synchronize a new object."""
        entry = self.metadata.getentry(fspath)
        if entry:
            create_object(container, name, entry, fspath)
            obj = traverseName(container, name)
            adapter = get_adapter(obj)
            if IObjectDirectory.isImplementedBy(adapter):
                self.synch_dir(obj, fspath)

    def synch_old(self, container, name, fspath):
        """Helper to synchronize an existing object."""
        entry = self.metadata.getentry(fspath)
        if entry.get("flag") == "removed":
            delete_item(container, name)
            return
        obj = traverseName(container, name)
        adapter = get_adapter(obj)
        if IObjectDirectory.isImplementedBy(adapter):
            self.synch_dir(obj, fspath)
        else:
            if adapter.typeIdentifier() != entry.get("type"):
                create_object(container, name, entry, fspath, replace=True)
            else:
                curdata = adapter.getBody()
                newdata = read_file(fspath)
                if newdata != curdata:
                    adapter.setBody(newdata)
                    # Now publish an event, but not for annotations or
                    # extras.  To know which case we have, see if
                    # objectName() works.  XXX This is a hack.
                    try:
                        objectName(obj)
                    except:
                        pass
                    else:
                        publish(obj, ObjectModifiedEvent(obj))

# Functions below this point are all helpers and not part of the
# API offered by this module.  They can be functions because they
# don't use the metadata database or add to the list of conflicts.

def create_object(container, name, entry, fspath, replace=False):
    """Helper to create an item in a container or mapping."""
    factory_name = entry.get("factory")
    if factory_name:
        # A given factory overrides everything
        factory = resolve(factory_name)
        obj = factory()
    else:
        # No factory; try using IFileFactory or IDirectoryFactory
        as = getService(container, "Adapters")
        isuffix = name.rfind(".")
        if isuffix >= 0:
            suffix = name[isuffix:]
        else:
            suffix = "."

        if os.path.isdir(fspath):
            iface = IDirectoryFactory
        else:
            iface = IFileFactory

        factory = as.queryNamedAdapter(container, iface, suffix)
        if factory is None:
            factory = as.queryAdapter(container, iface)

        if iface is IDirectoryFactory:
            if factory:
                obj = factory(name)
                obj = removeAllProxies(obj)
            else:
                raise SynchronizationError(
                    "don't know how to create a directory",
                    container,
                    name)
        else:
            if factory:
                data = read_file(fspath)
                obj = factory(name, None, data)
                obj = removeAllProxies(obj)
            else:
                # Oh well, assume the file is an xml pickle
                obj = load_file(fspath)

    set_item(container, name, obj, replace)

def set_item(container, name, obj, replace=False):
    """Helper to set an item in a container or mapping."""
    if IContainer.isImplementedBy(container):
        if not replace:
            publish(container, ObjectCreatedEvent(obj))
        container = getAdapter(container, IZopeContainer)
        if replace:
            del container[name]
        newname = container.setObject(name, obj)
        if newname != name:
            raise SynchronizationError(
                "Container generated new name for %s (new name %s)" %
                (name, newname))
    else:
        # Not a container, must be a mapping
        # (This is used for extras and annotations)
        container[name] = obj

def delete_item(container, name):
    """Helper to delete an item from a container or mapping."""
    if IContainer.isImplementedBy(container):
        container = getAdapter(container, IZopeContainer)
    del container[name]

def load_file(fspath):
    """Helper to load an xml pickle from a file."""
    return loads(read_file(fspath, "r"))

def read_file(fspath, mode="rb"):
    """Helper to read the data from a file."""
    assert mode in ("r", "rb")
    f = open(fspath, mode)
    try:
        data = f.read()
    finally:
        f.close()
    return data

def get_adapter(obj):
    """Helper to get the special fssync adapter."""
    syncService = getService(obj, 'FSRegistryService')
    return syncService.getSynchronizer(obj)
