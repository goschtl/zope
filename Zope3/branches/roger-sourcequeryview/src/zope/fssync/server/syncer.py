##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Basic server-side synchronizer.

$Id$
"""
import os

from zope.fssync import metadata
from zope.fssync.server.interfaces import IObjectDirectory, IObjectFile


def writeFile(data, path, mode="wb"):
    f = open(path, mode)
    try:
        f.write(data)
    finally:
        f.close()


class Syncer(object):

    def __init__(self, getObjectId, getSerializer,
                 getAnnotations=lambda obj: None):
        self._metadata = metadata.Metadata()
        self.getObjectId = getObjectId
        self.getSerializer = getSerializer
        self.getAnnotations = getAnnotations

    def toFS(self, ob, name, location):
        """Check an object out to the file system

        ob -- The object to be checked out

        name -- The name of the object

        location -- The directory on the file system where the object will go
        """

        # Get name path and check that name is not an absolute path
        path = os.path.join(location, name)
        if path == name:
            raise ValueError("Invalid absolute path name")

        mdmanager = self._metadata.getmanager(location)

        # Look for location admin dir
        if not os.path.exists(mdmanager.zdir):
            os.mkdir(mdmanager.zdir)

        self.dumpTree(ob, name, path, mdmanager)

    def dumpTree(self, ob, name, path, mdmanager):
        entry = mdmanager.getentry(name)

        # Get the object adapter
        adapter = self.getSerializer(ob)

        entry.clear()
        entry['type'] = adapter.typeIdentifier()
        entry['factory'] = adapter.factory()

        try:
            objectPath = self.getObjectId(ob)
        except (TypeError, KeyError):
            # this case can be triggered for persistent objects that don't
            # have a name in the content space (annotations, extras)
            pass
        else:
            entry['path'] = objectPath

        # Write entries file
        mdmanager.flush()

        # Handle extras
        extra = adapter.extra()
        if extra:
            extra_dir, mdextra = self.createManagedDirectory(
                mdmanager.zdir, 'Extra', name)
            for ename in extra:
                # @@Zope/Extra/<name>/<ename>
                edata = extra[ename]
                self.dumpTree(edata,
                              ename,
                              os.path.join(extra_dir, ename),
                              mdextra)

        # Handle annotations
        annotations = self.getAnnotations(ob)
        if annotations is not None:
            annotation_dir, mdannotations = self.createManagedDirectory(
                mdmanager.zdir, 'Annotations', name)
            for key in annotations:
                # @@Zope/Annotations/<name>/<key>
                annotation = annotations[key]
                self.dumpTree(annotation,
                              key,
                              os.path.join(annotation_dir, key),
                              mdannotations)

        # Handle data
        if IObjectFile.providedBy(adapter):
            # File
            assert not IObjectDirectory.providedBy(adapter)
            writeFile(adapter.getBody(), path)
        else:
            # Directory
            assert IObjectDirectory.providedBy(adapter)
            if not os.path.exists(path):
                os.mkdir(path)
            mdmanager = self._metadata.getmanager(path)
            mdmanager.ensure()

            for cname, cob in adapter.contents():
                cpath = os.path.join(path, cname)
                self.dumpTree(cob, cname, cpath, mdmanager)

    def createManagedDirectory(self, base, *parts):
        dir = base
        for p in parts:
            dir = os.path.join(dir, p)
            if not os.path.exists(dir):
                os.mkdir(dir)
        return dir, self._metadata.getmanager(dir)
