##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Filesystem synchronization functions.

$Id: syncer.py,v 1.20 2003/05/25 06:19:09 gvanrossum Exp $
"""

import os

from zope.component import queryAdapter, getService
from zope.xmlpickle import dumps, loads
from zope.app.interfaces.fssync \
     import IObjectEntry, IObjectDirectory, IObjectFile

from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.container import IContainer
from zope.configuration.name import resolve
from zope.app.fssync.classes import Default
from zope.app.traversing import getPath
from zope.app.fssync.fsregistry import getSynchronizer
from zope.app.interfaces.file import IFileFactory
from zope.proxy.introspection import removeAllProxies

def readFile(path):
    f = open(path)
    try:
        return f.read()
    finally:
        f.close()

def writeFile(data, path):
    f = open(path, "w")
    try:
        f.write(data)
    finally:
        f.close()

def loadFile(path):
    return loads(readFile(path))

def dumpFile(obj, path):
    writeFile(dumps(obj), path)

def toFS(ob, name, location):
    """Check an object out to the file system

    ob -- The object to be checked out

    name -- The name of the object

    location -- The directory on the file system where the object will go
    """

    # Get name path and check that name is not an absolute path
    path = os.path.join(location, name)
    if path == name:
        raise ValueError("Invalid absolute path name")

    # Look for location admin dir
    admin_dir = os.path.join(location, '@@Zope')
    if not os.path.exists(admin_dir):
        os.mkdir(admin_dir)

    # Open Entries file
    entries_path = os.path.join(admin_dir, "Entries.xml")
    if os.path.exists(entries_path):
        entries = loadFile(entries_path)
    else:
        entries = {}

    # Get the object adapter
    syncService = getService(ob, 'FSRegistryService')
    adapter = syncService.getSynchronizer(ob)

    entries[name] = {'type': adapter.typeIdentifier(),
                     'factory': adapter.factory(),
                     }

    try:
        objectPath = str(getPath(ob))
    except (TypeError, KeyError):
        objectPath = ''
    else:
        entries[name]['path'] = objectPath

    # Write entries file
    dumpFile(entries, entries_path)

    # Handle extras
    extra = adapter.extra()
    if extra:
        extra_dir = os.path.join(admin_dir, 'Extra')
        if not os.path.exists(extra_dir):
            os.mkdir(extra_dir)
        extra_dir = os.path.join(extra_dir, name)
        if not os.path.exists(extra_dir):
            os.mkdir(extra_dir)
        for ename in extra:
            edata = extra[ename]
            toFS(edata, ename, extra_dir)

    # Handle annotations
    annotations = queryAdapter(ob, IAnnotations)
    if annotations is not None:
        annotation_dir = os.path.join(admin_dir, 'Annotations')
        if not os.path.exists(annotation_dir):
            os.mkdir(annotation_dir)
        annotation_dir = os.path.join(annotation_dir, name)
        if not os.path.exists(annotation_dir):
            os.mkdir(annotation_dir)
        for key in annotations:
            annotation = annotations[key]
            toFS(annotation, key, annotation_dir)

    # Handle data
    if IObjectFile.isImplementedBy(adapter):
        # File
        data = ''
        if not os.path.exists(path):
            data = adapter.getBody()
            writeFile(data, path)
    else:
        # Directory
        assert IObjectDirectory.isImplementedBy(adapter)
        if os.path.exists(path):
            dir_entries = os.path.join(path, '@@Zope', 'Entries.xml')
            if os.path.exists(dir_entries):
                dumpFile({}, dir_entries)
        else:
            os.mkdir(path)

        for cname, cob in adapter.contents():
            toFS(cob, cname, path)


class SynchronizationError(Exception):
    pass


def _setItem(container, name, ob, old=False):
    # Set an item in a container or in a mapping
    if IContainer.isImplementedBy(container):
        if old:
            del container[name]
        newName = container.setObject(name, ob)
        if newName != name:
            raise SynchronizationError(
                "Container generated new name for %s (new name %s)" %
                (name, newName))
    else:
        # Not a container, must be a mapping
        container[name] = ob


def _create(container, name, factory, path, old=False):
    # Create an item in a container or in a mapping
    if factory:
        # A given factory overrides everything
        newOb = resolve(factory)()
    else:
        # No factory; try using the newfangled IFileFactory feature
        as = getService(container, "Adapters")
        isuffix = name.rfind(".")
        if isuffix >= 0:
            suffix = name[isuffix:]
        else:
            suffix = "."
            
        factory = as.queryNamedAdapter(container, IFileFactory, suffix)
        if factory is None:
            factory = as.queryAdapter(container, IFileFactory)

        if factory:
            newOb = factory(name, None, readFile(path))
            newOb = removeAllProxies(newOb)
        else:
            # Oh well, do it the oldfashioned way
            newOb = loadFile(path)

    _setItem(container, name, newOb, old)

    return newOb


def fromFS(container, name, location):
    """Synchromize a file from what's on the file system.

    container -- parent of new object

    name -- name of new object in container

    location -- filesystem directory containing name
    """
    if not name:
        # Special case: loading the root folder.
        # Don't make changes to the root, but change everything underneath.
        path = os.path.join(location, "root")
        if not os.path.isdir(path):
            raise SynchronizationError("root folder not found")

        dir_entries_path = os.path.join(path, '@@Zope', 'Entries.xml')
        if os.path.exists(dir_entries_path):
            dir_entries = loadFile(dir_entries_path)
        else:
            dir_entries = {}
        for cname in dir_entries:
            fromFS(container, cname, path)

        return

    # Look for location admin dir
    admin_dir = os.path.join(location, '@@Zope')
    if not os.path.exists(admin_dir):
        raise SynchronizationError("No @@Zope admin directory, %s" % admin_dir)

    # Open Entries file
    entries_path = os.path.join(admin_dir, "Entries.xml")
    entries = loadFile(entries_path)
    entry = entries[name]
    factory = entry.get('factory')

    # Get name path and check that name is not an absolute path
    path = os.path.join(location, name)
    if path == name:
        raise ValueError("Invalid absolute path name")

    # See if this is an existing object
    if name not in container:
        # Not there; we need to create a new object
        assert entry.get("flag") == "added", name
        newOb = _create(container, name, factory, path)

    else:
        # It's there; let's see if we need to delete it
        if entry.get("flag") == "removed":
            del container[name]
            return # That was easy!

        # No, updating.  Let's see if we have the same kind of object

        # Get the object adapter
        ob = container[name]
        syncService = getService(ob, 'FSRegistryService')
        adapter = syncService.getSynchronizer(ob)

        # Replace the object if the type is different
        if adapter.typeIdentifier() != entry.get('type'):
            # We have a different object, replace the one that's there

            newOb = _create(container, name, factory, path, old=True)

        elif not factory:
            if entry.get('type') == '__builtin__.str':
                newOb = readFile(path)
                _setItem(container, name, newOb, old=True)
            else:
                # Special case pickle data
                oldOb = container[name]
                oldOb = removeAllProxies(oldOb)
                newOb = loadFile(path)
                try:
                    # See if we can and should just copy the state
                    oldOb._p_oid # Is it persistent?
                    getstate = newOb.__getstate__
                except AttributeError:
                    # Nope, we have to replace
                    _setItem(container, name, newOb, old=True)
                else:
                    oldOb.__setstate__(getstate())
                    oldOb._p_changed = True
        # XXX else, what?

    # Get the object adapter again
    ob = container[name]
    syncService = getService(ob, 'FSRegistryService')
    adapter = syncService.getSynchronizer(ob)

    # Handle extra
    extra = adapter.extra()
    extra_dir = os.path.join(admin_dir, 'Extra', name)
    extra_entries_path = os.path.join(extra_dir, "@@Zope", "Entries.xml")
    if extra:
        if not os.path.exists(extra_entries_path):
            if entry.get("flag") != "added":
                # The file system has no extras, so delete all of the
                # object's extras.
                for key in list(extra):
                    del extra[key]
        else:
            extra_entries = loadFile(extra_entries_path)
            for ename in extra_entries:
                fromFS(extra, ename, extra_dir)
    elif os.path.exists(extra_entries_path):
        extra_entries = loadFile(extra_entries_path)
        if extra_entries:
            raise SynchronizationError(
                "File-system extras for object with no extra data")

    # Handle annotations
    annotations = queryAdapter(ob, IAnnotations)
    annotation_dir = os.path.join(admin_dir, 'Annotations', name)
    annotation_entries_path = os.path.join(
        annotation_dir, "@@Zope", "Entries.xml")
    if annotations is not None:
        if not os.path.exists(annotation_entries_path):
            if entry.get("flag") != "added":
                # The file system has no annotations, so delete all of
                # the object's annotations.
                for key in list(annotations):
                    del annotations[key]
        else:
            annotation_entries = loadFile(annotation_entries_path)
            for ename in annotation_entries:
                fromFS(annotations, ename, annotation_dir)
    elif os.path.exists(annotation_entries_path):
        annotation_entries = loadFile(annotation_entries_path)
        if annotation_entries:
            raise SynchronizationError(
                "File-system annotations for non annotatable object")

    # Handle data
    if IObjectFile.isImplementedBy(adapter):
        # File
        if os.path.isdir(path):
            raise SynchronizationError("Object is file, but data is directory")
        adapter.setBody(readFile(path))

    else:
        # Directory
        assert IObjectDirectory.isImplementedBy(adapter)
        if not os.path.isdir(path):
            raise SynchronizationError("Object is directory, but data is file")

        dir_entries_path = os.path.join(path, '@@Zope', 'Entries.xml')
        if os.path.exists(dir_entries_path):
            dir_entries = loadFile(dir_entries_path)
        else:
            dir_entries = {}
        for cname in dir_entries:
            fromFS(ob, cname, path)
