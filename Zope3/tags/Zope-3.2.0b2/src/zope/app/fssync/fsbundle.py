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
"""High-level class to support bundle management on an fssync checkout.

$Id$
"""
__docformat__ = 'restructuredtext'

import os

from zope.fssync.copier import ObjectCopier
from zope.fssync.fssync import FSSync
from zope.fssync.fsutil import Error
from zope.fssync.metadata import Metadata

BUNDLE_TYPE = "zope.app.services.bundle.Bundle"
FOLDER_TYPE = "zope.app.component.site.SiteManagementFolder"


class FSBundle(object):

    def __init__(self):
        self.metadata = Metadata()
        self.sync = FSSync(metadata=self.metadata)

    # bundle operations

    def create(self, path, type, factory, source=None):
        if os.path.exists(path):
            raise Error("%r already exists", path)
        dir, name = os.path.split(path)
        self.check_name(name)
        self.check_directory(dir)
        self.check_directory_known(dir)
        if source is not None:
            self.check_source(source, BUNDLE_TYPE, FOLDER_TYPE)
            if type is None and factory is None:
                srctype, srcfactory = self.metadata.gettypeinfo(source)
                if srctype == FOLDER_TYPE:
                    factory = type = BUNDLE_TYPE
                else:
                    # source is already a bundle; create the same type
                    type = srctype
                    factory = srcfactory
        elif factory is None and type is None:
            factory = type = BUNDLE_TYPE
        if source is None:
            self.sync.mkdir(path)
        else:
            copier = ObjectCopier(self.sync)
            copier.copy(source, path, children=True)
        self.settypeinfo(path, type, factory)

    def unpack(self, source, target):
        # source identifies the bundle to unpack
        # target identifies a location to unpack to
        if os.path.exists(target):
            target_dir = target
            # compute target name from prefix of source
            pass
            target = os.path.join(target_dir, target_name)
        else:
            target_dir, target_name = os.path.split(target)
        self.check_source(source, BUNDLE_TYPE)
        self.check_directory_known(target_dir)
        # ...
        self.settypeinfo(target, FOLDER_TYPE, FOLDER_TYPE)

    # helper methods

    def settypeinfo(self, path, type, factory):
        entry = self.metadata.getentry(path)
        assert entry.get("flag") == "added"
        # override any existing type and factory
        entry["factory"] = factory
        entry["type"] = type
        self.metadata.flush()

    def check_source(self, source, *allowed_types):
        # make sure the source is a site-management folder or a bundle
        if not os.path.exists(source):
            raise Error("%r does not exist", source)
        if not os.path.isdir(source):
            raise Error("%r must be a directory", source)
        self.check_directory_known(os.path.dirname(source))
        self.check_directory_known(source)
        type, factory = self.metadata.gettypeinfo(source)
        if type == BUNDLE_TYPE:
            pass
        elif type == FOLDER_TYPE:
            pass
        else:
            # don't know; play it safe
            raise Error(
                "%r doesn't appear to be a bundle or site-management folder",
                source)

    def check_directory(self, dir):
        if dir:
            if not os.path.exists(dir):
                raise Error("%r does not exist", dir)
            if not os.path.isdir(dir):
                raise Error("%r is not a directory", dir)
        # else: os.curdir assumed

    def check_directory_known(self, dir):
        dir = dir or os.curdir
        entry = self.metadata.getentry(dir)
        if not entry:
            raise Error("nothing known about", dir)

    def check_name(self, name):
        if name.count("-") != 1:
            raise Error("%r is not a legal bundle name", name)
        basename, version = name.split("-")
        self.check_version(version)

    def check_version(self, s):
        parseBundleVersion(s)


def parseBundleVersion(s):
    parts = s.split(".")
    if len(parts) not in (3, 4):
        raise Error("%r is not a valid bundle version", s)
    try:
        n0 = int(parts[0])
        n1 = int(parts[1])
        n2 = int(parts[2])
    except ValueError:
        raise Error("%r is not a valid bundle version", s)
    try:
        p3 = int(parts[3])
    except IndexError:
        p3 = None
    except ValueError:
        p3 = parts[3]
    return (n0, n1, n2, p3)
