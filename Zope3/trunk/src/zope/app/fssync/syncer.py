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

$Id: syncer.py,v 1.22 2003/05/28 15:46:08 jim Exp $
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
from zope.proxy import removeAllProxies

def readFile(path, mode="rb"):
    f = open(path, mode)
    try:
        return f.read()
    finally:
        f.close()

def writeFile(data, path, mode="wb"):
    f = open(path, mode)
    try:
        f.write(data)
    finally:
        f.close()

def loadFile(path):
    return loads(readFile(path, "r"))

def dumpFile(obj, path):
    writeFile(dumps(obj), path, "w")

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
