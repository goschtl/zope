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

$Id: syncer.py,v 1.2 2003/05/05 18:01:01 gvanrossum Exp $
"""

import os, string

from zope.component import queryAdapter, getService
from zope.xmlpickle.xmlpickle import dumps, loads
from zope.app.interfaces.fssync \
     import IObjectEntry, IObjectDirectory, IObjectFile

from zope.app.interfaces.annotation import IAnnotations
from zope.app.interfaces.container import IContainer
from zope.configuration.name import resolve
from zope.app.fssync.classes import Default
from zope.app.traversing import getPath
from zope.app.fssync.fsregistry import getSynchronizer

def toFS(ob, name, location, mode=None, objpath=None):
    """Check an object out to the file system

    ob -- The object to be checked out

    name -- The name of the object

    location -- The directory on the file system where the object will go
    """
    objectPath = ''
    # Look for location admin dir
    admin_dir = os.path.join(location, '@@Zope')
    if not os.path.exists(admin_dir):
        os.mkdir(admin_dir)

    # Open Entries file
    entries_path = os.path.join(admin_dir, "Entries.xml")
    if os.path.exists(entries_path):
        entries = loads(open(entries_path).read())
    else:
        entries = {}

    # Get the object adapter
    syncService = getService(ob, 'FSRegistryService')
    adapter = syncService.getSynchronizer(ob)

    entries[name] = {'type': adapter.typeIdentifier(),
                     'factory': adapter.factory(),
                     }

    try:
        if mode == 'N' or mode == 'D':
            objectPath = objpath
            entries[name]['isNew'] = 'Y'
        else:
            objectPath = str(getPath(ob))
        entries[name]['path'] = objectPath
    except TypeError:
        pass

    # Write entries file
    open(entries_path, 'w').write(dumps(entries))


    # Get name path and check that name is not an absolute path
    path = os.path.join(location, name)
    if path == name:
        raise ValueError("Invalid absolute path name")


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
        data = ''
        if mode !='C': # is None:
            if os.path.exists(path):
                f = open(path, 'r')
                data = f.read()
                f.close()
                open(path, 'w').write(string.strip(data))
            else:
                open(path, 'w').write(string.strip(adapter.getBody()))
            if objectPath:
                print 'U %s' % (objectPath[1:])
        original_path = os.path.join(admin_dir, 'Original')
        if not os.path.exists(original_path):
            os.mkdir(original_path)
        original_path = os.path.join(original_path, name)
        if data:
            open(original_path, 'w').write(string.strip(data))
        else:
            open(original_path, 'w').write(string.strip(adapter.getBody()))


    else:
        # Directory
        if objectPath:
            print 'UPDATING %s' % (objectPath[1:])
        if os.path.exists(path):
            dir_entries = os.path.join(path, '@@Zope', 'Entries.xml')
            if os.path.exists(dir_entries):
                open(dir_entries, 'w').write(dumps({}))
            elif mode == 'D':
                admin_dir = os.path.join(path, '@@Zope')
                os.mkdir(admin_dir)
                open(dir_entries, 'w').write(dumps({}))
        else:
            os.mkdir(path)
            if mode == 'D':
                admin_dir = os.path.join(path, '@@Zope')
                os.mkdir(admin_dir)
                dir_entries = os.path.join(path, '@@Zope', 'Entries.xml')
                open(dir_entries, 'w').write(dumps({}))

        for cname, cob in  adapter.contents():
            toFS(cob, cname, path)


class SynchronizationError(Exception):
    pass


def _setItem(container, name, ob, old=0):
    # Set an item in a container or in a mapping
    if IContainer.isImplementedBy(container):
        if old:
            del container[name]
        newName = container.setObject(name, ob)
        if newName != name:
            raise SynchronizationError(
                "Container generated new name for %s" % path)
    else:
        # Not a container, must be a mapping
        container[name] = ob


def fromFS(container, name, location, mode=None):
    """Synchromize a file from what's on the file system.
    """
    msg =''
    objectPath = ''
    # Look for location admin dir
    admin_dir = os.path.join(location, '@@Zope')
    if not os.path.exists(admin_dir):
        raise SynchronizationError("No @@Zope admin directory, %s" % admin_dir)

    # Open Entries file
    entries_path = os.path.join(admin_dir, "Entries.xml")
    entries = loads(open(entries_path).read())
    entry = entries[name]
    factory = entry.get('factory')

    # Get name path and check that name is not an absolute path
    path = os.path.join(location, name)
    if path == name:
        raise ValueError("Invalid absolute path name")


    # See if this is an existing object
    if name in container:
        # Yup, let's see if we have the same kind of object

        # Get the object adapter
        ob = container[name]
        syncService = getService(ob, 'FSRegistryService')
        adapter = syncService.getSynchronizer(ob)


        # Replace the object if the type is different
        if adapter.typeIdentifier() != entry.get('type'):
            # We have a different object, replace the one that's there

            if factory:
                newOb = resolve(factory)()
            else:
                newOb = loads(open(path).read())

            _setItem(container, name, newOb, old=1)

        elif not factory:
            if entry.get('type') == '__builtin__.str':
                newOb = open(path).read()
                _setItem(container, name, newOb, old=1)
            else:
                # Special case pickle data
                oldOb = container[name]
                newOb = loads(open(path).read())
                try:
                    # See if we can and should just copy the state
                    oldOb._p_oid # Is it persisteny
                    getstate = newOb.__getstate__
                except AttributeError:
                    # Nope, we have to replace.
                    _setItem(container, name, newOb, old=1)
                else:
                    oldOb.__setstate__(getstate())
                    oldOb._p_changed = 1


    else:
        # We need to create a new object
        if factory:
            newOb = resolve(entry['factory'])()
        else:
            newOb = loads(open(path).read())

        _setItem(container, name, newOb)


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
            # The file system has no extras, so delete all of the object's
            # extras.
            for key in extra:
                del extra[key]
        else:
            extra_entries = loads(
                open(extra_entries_path).read())
            for ename in extra_entries:
                fromFS(extra, ename, extra_dir, mode)
    elif os.path.exists(extra_entries_path):
        extra_entries = loads(
            open(extra_entries_path).read())
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
            # The file system has no annotations, so delete all of the object's
            # annotations.
            for key in annotations:
                del annotations[key]
        else:
            annotation_entries = loads(
                open(annotation_entries_path).read())
            for ename in annotation_entries:
                fromFS(annotations, ename, annotation_dir, mode)
    elif os.path.exists(annotation_entries_path):
        annotation_entries = loads(
            open(annotation_entries_path).read())
        if annotation_entries:
            raise SynchronizationError(
                "File-system annotations for non annotatable object")

    # Handle data
    if IObjectFile.isImplementedBy(adapter):
        # File
        if os.path.isdir(path):
            raise SynchronizationError("Object is file, but data is directory")
        adapter.setBody(open(path).read())
        if mode is not None and mode != 'T':
            if string.find(path,'@@Zope')==-1:
                #copying to original
                fspath = path
                f = open(fspath, 'r')
                data = f.read()
                f.close()
                original_path = os.path.join(os.path.dirname(fspath),'@@Zope','Original',os.path.basename(fspath))
                f = open(original_path, 'w')
                f.write(string.strip(data))
                f.close()
                entries_path = os.path.join(os.path.dirname(fspath),'@@Zope','Entries.xml')
                entries = loads(open(entries_path).read())
                if entries[os.path.basename(fspath)].has_key('isNew'):
                    del entries[os.path.basename(fspath)]['isNew']
                    open(entries_path, 'w').write(dumps(entries))
                objectpath = entries[os.path.basename(fspath)]['path']
                msg = "%s  <--  %s" %(objectpath, string.split(objectpath,'/')[-1])
                print msg


    else:
        # Directory
        if not os.path.isdir(path):
            raise SynchronizationError("Object is directory, but data is file")

        if mode != 'T':
            entries_path = os.path.join(os.path.dirname(path),'@@Zope','Entries.xml')
            entries = loads(open(entries_path).read())
            if entries[os.path.basename(path)].has_key('isNew'):
                del entries[os.path.basename(path)]['isNew']
                open(entries_path, 'w').write(dumps(entries))

        dir_entries_path = os.path.join(path, '@@Zope', 'Entries.xml')
        dir_entries = loads(open(dir_entries_path).read())
        for cname in dir_entries:
            fromFS(ob, cname, path, mode)
