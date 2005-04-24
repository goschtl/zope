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
"""Commit changes from the filesystem.

$Id$
"""
__docformat__ = 'restructuredtext'

import os

from zope.configuration.name import resolve
from zope.fssync import fsutil
from zope.fssync.metadata import Metadata
from zope.fssync.server.interfaces import IObjectDirectory, IObjectFile
from zope.proxy import removeAllProxies
from zope.xmlpickle import fromxml

from zope.app import zapi
from zope.app.fssync import fspickle
from zope.app.container.interfaces import IContainer
from zope.app.container.interfaces import IContainer
from zope.app.traversing.api import traverseName, getName
from zope.app.filerepresentation.interfaces import IFileFactory
from zope.app.filerepresentation.interfaces import IDirectoryFactory
from zope.event import notify
from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.event.objectevent import ObjectModifiedEvent
from zope.app.container.contained import contained

class SynchronizationError(Exception):
    pass

class Checker(object):
    """Check that the filesystem is consistent with the object database.

    The public API consists of `__init__()`, `check()` and `errors()` only.
    """

    def __init__(self,
                 getSerializer,
                 metadata=None,
                 raise_on_conflicts=False,
                 getAnnotations=lambda obj: None,
                 ):
        """Constructor.  Optionally pass a metadata database."""
        if metadata is None:
            metadata = Metadata()
        self.metadata = metadata
        self.raise_on_conflicts = raise_on_conflicts
        self.conflicts = []
        self.getSerializer = getSerializer
        self.getAnnotations = getAnnotations

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

    def conflict(self, fspath):
        """Helper to report a conflict.

        Conflicts can be retrieved by calling `errors()`.
        """
        if self.raise_on_conflicts:
            raise SynchronizationError(fspath)
        if fspath not in self.conflicts:
            self.conflicts.append(fspath)

    def check(self, container, name, fspath):
        """Compare an object or object tree from the filesystem.

        If the originals on the filesystem are not uptodate, errors
        are reported by calling `conflict()`.

        Invalid object names are reported by raising
        ``SynchronizationError``.
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
                adapter = self.getSerializer(obj)
                extra = adapter.extra()
                extrapath = fsutil.getextra(fspath)
                if extra is not None and os.path.exists(extrapath):
                    self.check_dir(extra, extrapath)
                ann = self.getAnnotations(obj)
                annpath = fsutil.getannotations(fspath)
                if ann is not None and os.path.exists(annpath):
                    self.check_dir(ann, annpath)

    def check_dir(self, container, fspath):
        """Helper to check a directory."""
        adapter = self.getSerializer(container)
        nameset = {}
        if IObjectDirectory.providedBy(adapter):
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
        adapter = self.getSerializer(obj)
        if IObjectDirectory.providedBy(adapter):
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

class Committer(object):
    """Commit changes from the filesystem to the object database.

    The filesystem's originals must consistent with the object
    database; this should be checked beforehand by a `Checker` instance
    with the same arguments.

    The public API consists of `__init__()` and `synch()` only.
    """

    def __init__(self, getSerializer, metadata=None,
                 getAnnotations=lambda obj: None):
        """Constructor.  Optionally pass a metadata database."""
        self.getSerializer = getSerializer
        self.getAnnotations = getAnnotations
        if metadata is None:
            metadata = Metadata()
        self.metadata = metadata

    # The Extra and Annotations directories of a zsync need to be
    # treated specially to allow create_object() to use the the
    # innermost object 'o' from which the root is reachable via
    # __parent__ references to perform location-sensitive operations.
    # This is the only way these objects can perform adapter looks or
    # resolve persistent references to objects in the tree.  They will
    # (still) not be able to resolve "parent" references because the
    # extra and annotation values for object 'o' have no parent.
    #
    # This passes around a context object once traversal has entered
    # the extra and annotation areas of the data area.  This object is
    # used to provide location if not None; it is only checked by
    # create_object().

    def synch(self, container, name, fspath, context=None):
        """Synchronize an object or object tree from the filesystem.

        ``SynchronizationError`` is raised for errors that can't be
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
            self.synch_dir(container, fspath, context)
        else:
            try:
                traverseName(container, name)
            except:
                self.synch_new(container, name, fspath, context)
            else:
                self.synch_old(container, name, fspath, context)

            # Now update extra and annotations
            try:
                obj = traverseName(container, name)
            except:
                pass
            else:
                adapter = self.getSerializer(obj)
                extra = adapter.extra()
                extrapath = fsutil.getextra(fspath)
                if extra is not None and os.path.exists(extrapath):
                    self.synch_dir(extra, extrapath, obj)
                ann = self.getAnnotations(obj)
                annpath = fsutil.getannotations(fspath)
                if ann is not None and os.path.exists(annpath):
                    self.synch_dir(ann, annpath, obj)

    def synch_dir(self, container, fspath, context=None):
        """Helper to synchronize a directory."""
        adapter = self.getSerializer(container)
        nameset = {} # name --> absolute path
        if IObjectDirectory.providedBy(adapter):
            for name, obj in adapter.contents():
                nameset[name] = os.path.join(fspath, name)
        else:
            # Annotations, Extra
            for name in container:
                nameset[name] = os.path.join(fspath, name)
        for name in self.metadata.getnames(fspath):
            nameset[name] = os.path.join(fspath, name)
        # Sort the list of keys for repeatability
        names_paths = nameset.items()
        names_paths.sort()
        subdirs = []
        # Do the non-directories first.
        # This ensures that the objects are created before dealing
        # with Annotations/Extra for those objects.
        for name, path in names_paths:
            if os.path.isdir(path):
                subdirs.append((name, path))
            else:
                self.synch(container, name, path, context)
        # Now do the directories
        for name, path in subdirs:
            self.synch(container, name, path, context)

    def synch_new(self, container, name, fspath, context=None):
        """Helper to synchronize a new object."""
        entry = self.metadata.getentry(fspath)
        if entry:
            self.create_object(container, name, entry, fspath,
                               context=context)
            obj = traverseName(container, name)
            adapter = self.getSerializer(obj)
            if IObjectDirectory.providedBy(adapter):
                self.synch_dir(obj, fspath, context)

    def synch_old(self, container, name, fspath, context=None):
        """Helper to synchronize an existing object."""
        entry = self.metadata.getentry(fspath)
        if entry.get("flag") == "removed":
            delete_item(container, name)
            return
        if not entry:
            # This object was not included on the filesystem; skip it
            return
        obj = traverseName(container, name)
        adapter = self.getSerializer(obj)
        if IObjectDirectory.providedBy(adapter):
            self.synch_dir(obj, fspath, context)
        else:
            if adapter.typeIdentifier() != entry.get("type"):
                self.create_object(container, name, entry, fspath,
                                   replace=True, context=context)
            else:
                original_fn = fsutil.getoriginal(fspath)
                if os.path.exists(original_fn):
                    olddata = read_file(original_fn)
                else:
                    # value appears to exist in the object tree, but
                    # may have been created as a side effect of an
                    # addition in the parent; this can easily happen
                    # in the extra or annotation data for an object
                    # copied from another using "zsync copy" (for
                    # example)
                    olddata = None
                newdata = read_file(fspath)
                if newdata != olddata:
                    if not entry.get("factory"):
                        # If there's no factory, we can't call setBody()
                        self.create_object(container, name, entry, fspath,
                                           True, context=context)
                        obj = traverseName(container, name)
                    else:
                        adapter.setBody(newdata)
                    # Now publish an event, but not for annotations or
                    # extras.  To know which case we have, see if
                    # getName() works.  XXX This is a hack.
                    try:
                        getName(obj)
                    except:
                        pass
                    else:
                        notify(ObjectModifiedEvent(obj))

    def create_object(self, container, name, entry, fspath, replace=False,
                      context=None):
        """Helper to create an item in a container or mapping."""
        factory_name = entry.get("factory")
        if factory_name:
            # A given factory overrides everything
            factory = resolve(factory_name)
            obj = factory()
            obj = contained(obj, container, name=name)
            adapter = self.getSerializer(obj)
            if IObjectFile.providedBy(adapter):
                data = read_file(fspath)
                adapter.setBody(data)
        else:
            if context is None:
                location = container
                parent = container
            else:
                location = context
                parent = None

            # No factory; try using IFileFactory or IDirectoryFactory
            isuffix = name.rfind(".")
            if isuffix >= 0:
                suffix = name[isuffix:]
            else:
                suffix = "."

            if os.path.isdir(fspath):
                iface = IDirectoryFactory
            else:
                iface = IFileFactory

            factory = zapi.queryAdapter(location, iface, suffix)
            if factory is None:
                factory = iface(location, None)

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
                    # The file must contain an xml pickle, or we can't load it:
                    s = read_file(fspath)
                    s = fromxml(s)
                    obj = fspickle.loads(s, location, parent)

        set_item(container, name, obj, replace)

# Functions below this point are all helpers and not part of the
# API offered by this module.  They can be functions because they
# don't use the metadata database or add to the list of conflicts.

def set_item(container, name, obj, replace=False):
    """Helper to set an item in a container or mapping."""
    if IContainer.providedBy(container):
        if not replace:
            notify(ObjectCreatedEvent(obj))
        if replace:
            del container[name]

    container[name] = obj

def delete_item(container, name):
    """Helper to delete an item from a container or mapping."""
    del container[name]

def read_file(fspath):
    """Helper to read the data from a file."""
    f = open(fspath, "rb")
    try:
        data = f.read()
    finally:
        f.close()
    return data
