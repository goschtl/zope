##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Support for reading and writing PEP 262 package metadata files."""

import sets

from distutils.dist import DistributionMetadata

from zpkgtools import dependencies
from zpkgtools import publication


class PackageData(dependencies.DependencyInfo, DistributionMetadata):
    def __init__(self):
        super(PackageData, self).__init__()
        self.files = {}
        self.provides = sets.Set()

    def load(self, f):
        partsline = f.readline()
        parts = partsline.split()
        for part in parts:
            if part == "PKG-INFO":
                publication.load(f, metadata=self, versioninfo=True)
            elif part == "FILES":
                self.loadFiles(f)
            elif part == "REQUIRES":
                super(PackageData, self).load(f)
            elif part == "PROVIDES":
                self.loadProvides(f)
            else:
                # unsupported section; skip to next blank line
                for line in f:
                    if not line.strip():
                        break

    def loadFiles(self, f):
        while True:
            line = f.readline().strip()
            if not line:
                return
            parts = line.split("\t")
            while len(parts) < 6:
                parts.append(None)
            path, size, perms, owner, group, digest = parts[:6]
            try:
                size = int(size)
            except (TypeError, ValueError):
                # Ugh!  but we don't want to lose the info, so just keep it.
                pass
            if perms == "unknown":
                perms = None
            self.files[path] = FileEntry(path, size, perms,
                                         owner, group, digest)

    def loadProvides(self, f):
        while True:
            line = f.readline().strip()
            if not line:
                return
            self.provides.add(line)


class FileEntry(object):
    __slots__ = "path", "size", "permissions", "owner", "group", "digest"

    def __init__(self, path, size, permissions, owner, group, digest):
        self.path = path
        self.size = size
        self.permissions = permissions
        self.owner = owner
        self.group = group
        self.digest = digest
