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

$Id: committer.py,v 1.5 2003/05/29 18:04:26 gvanrossum Exp $
"""

import os
import shutil

from zope.component import queryAdapter, getService
from zope.xmlpickle import dumps, loads
from zope.configuration.name import resolve
from zope.proxy import removeAllProxies

from zope.fssync.metadata import Metadata
from zope.fssync import fsutil

from zope.app.interfaces.fssync \
     import IObjectEntry, IObjectDirectory, IObjectFile

from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.container import IContainer
from zope.app.fssync.classes import Default
from zope.app.traversing import getPath, traverseName
from zope.app.interfaces.file import IFileFactory, IDirectoryFactory

class SynchronizationError(Exception):
    pass

class Committer(object):
    """Commit changes from the filesystem to the object database.

    The filesystem's originals should be consistent with the object database.
    """

    def __init__(self, metadata=None):
        """Constructor.  Optionally pass a metadata database."""
        if metadata is None:
            metadata = Metadata()
        self.metadata = metadata
        self.conflicts = []

    def report_conflict(self, fspath):
        """Helper to report a conflict.

        Conflicts can be retrieved by calling get_errors().
        """
        if fspath not in self.conflicts:
            self.conflicts.append(fspath)

    def get_errors(self):
        """Get a list of errors (conflicts).

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

    def synch(self, container, name, fspath):
        """Synchronize an object or object tree from the filesystem.

        If the originals on the filesystem is not uptodate, errors are
        reported by calling report_conflict(), but no exception is
        raised unless something unexpected is wrong.

        SynchronizationError is raised for errors that can't be
        corrected by a update operation.
        """

        if (os.sep in name or
            (os.altsep and os.altsep in name) or
            name == os.curdir or
            name == os.pardir):
            # This name can't be mapped safely to the filesystem :-(
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
                adapter = self.get_adapter(obj)
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
        adapter = self.get_adapter(container)
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
            if entry.get("flag") != "added":
                self.report_conflict(fspath)
            else:
                del entry["flag"]
                if not os.path.exists(fspath):
                    self.report_conflict(fspath)
                    return
            self.create_object(container, name, entry, fspath)
            obj = traverseName(container, name)
            adapter = self.get_adapter(obj)
            if IObjectDirectory.isImplementedBy(adapter):
                self.synch_dir(obj, fspath)

    def synch_old(self, container, name, fspath):
        """Helper to synchronize an existing object."""
        entry = self.metadata.getentry(fspath)
        if "conflict" in entry:
            self.report_conflict(fspath)
        obj = traverseName(container, name)
        adapter = self.get_adapter(obj)
        if IObjectDirectory.isImplementedBy(adapter):
            self.synch_dir(obj, fspath)
            if entry.get("flag") == "removed":
                del container[name]
                entry.clear()
                self.remove_all(fspath)
        else:
            if entry.get("flag") == "added":
                self.report_conflict(fspath)
                del entry["flag"]
            oldfspath = fsutil.getoriginal(fspath)
            if not os.path.exists(oldfspath):
                self.report_conflict(fspath)
                olddata = None
            else:
                olddata = self.read_file(oldfspath)
                curdata = adapter.getBody()
                if curdata != olddata:
                    self.report_conflict(fspath)
            if entry.get("flag") == "removed":
                if os.path.exists(fspath):
                    self.report_conflict(fspath)
                del container[name]
                entry.clear()
                self.remove_all(fspath)
            else:
                if adapter.typeIdentifier() != entry.get("type"):
                    self.create_object(container, name, entry, fspath,
                                       replace=True)
                else:
                    newdata = self.read_file(fspath)
                    if newdata != olddata:
                        adapter.setBody(newdata)
                        newdata = adapter.getBody() # Normalize
                        self.write_file_and_original(newdata, fspath)

    def create_object(self, container, name, entry, fspath, replace=False):
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
                    data = self.read_file(fspath)
                    obj = factory(name, None, data)
                    obj = removeAllProxies(obj)
                else:
                    # Oh well, assume the file is an xml pickle
                    obj = self.load_file(fspath)

        self.set_item(container, name, obj, replace)

        adapter = self.get_adapter(obj)
        entry["type"] = adapter.typeIdentifier()
        entry["factory"] = adapter.factory()
        if "flag" in entry:
            del entry["flag"]
        if IObjectFile.isImplementedBy(adapter):
            newdata = adapter.getBody()
            self.write_file_and_original(newdata, fspath)

    def set_item(self, container, name, obj, replace=False):
        """Helper to set an item in a container or mapping."""
        if IContainer.isImplementedBy(container):
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

    def load_file(self, fspath):
        """Helper to load an xml pickle from a file."""
        return loads(self.read_file(fspath, "r"))

    def read_file(self, fspath, mode="rb"):
        """Helper to read the data from a file."""
        assert mode in ("r", "rb")
        f = open(fspath, mode)
        try:
            data = f.read()
        finally:
            f.close()
        return data

    def write_file_and_original(self, data, fspath, mode="wb"):
        """Helper to write data to a file *and* to its original."""
        self.write_file(data, fspath, mode)
        self.write_file(data, fsutil.getoriginal(fspath), mode)

    def write_file(self, data, fspath, mode="wb"):
        """Helper to write data to a file."""
        assert mode in ("w", "wb")
        head, tail = os.path.split(fspath)
        if not os.path.exists(head):
            os.makedirs(head)
        f = open(fspath, mode)
        try:
            f.write(data)
        finally:
            f.close()

    def remove_all(self, fspath):
        """Helper to remove a path and the corresponding original."""
        self.remove(fspath)
        self.remove(fsutil.getoriginal(fspath))
        self.remove(fsutil.getextra(fspath))
        self.remove(fsutil.getannotations(fspath))

    def remove(self, fspath):
        """Helper to remove a file or directory tree if it exists."""
        if os.path.isdir(fspath):
            shutil.rmtree(fspath)
        elif os.path.exists(fspath):
            os.remove(fspath)

    def get_adapter(self, obj):
        """Helper to get the special fssync adapter."""
        syncService = getService(obj, 'FSRegistryService')
        return syncService.getSynchronizer(obj)
