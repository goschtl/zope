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
"""High-level class to support bundle management on an fssync checkout.

$Id: fsbundle.py,v 1.1 2003/08/12 22:08:34 fdrake Exp $
"""

import os
import posixpath

from zope.fssync.fssync import FSSync
from zope.fssync.fsutil import Error
from zope.fssync.metadata import Metadata


class FSBundle(object):

    def __init__(self):
        self.metadata = Metadata()
        self.sync = FSSync(metadata=self.metadata)

    # bundle operations

    def create(self, path, type, factory):
        if os.path.exists(path):
            raise Error("%r already exists", path)
        dir, name = os.path.split(path)
        self.check_name(name)
        self.check_parent_directory(dir)
        if factory is None and type is None:
            factory = type = "zope.app.services.bundle.Bundle"
        self.sync.mkdir(path)
        entry = self.metadata.getentry(path)
        assert entry.get("flag") == "added"
        if factory:
            entry["factory"] = factory
        if type:
            entry["type"] = type
        self.metadata.flush()

    # helper methods

    def check_parent_directory(self, dir):
        if dir:
            if not os.path.exists(dir):
                raise Error("%r does not exist", dir)
            if not os.path.isdir(dir):
                raise Error("%r is not a directory", dir)
        else:
            dir = os.curdir
        # XXX this might not be the right check
        entry = self.metadata.getentry(dir)
        if not entry:
            raise Error("nothing known about", dir)

    def check_name(self, name):
        if name.count("-") != 1:
            raise Error("%r is not a legal bundle name", name)
        basename, version = name.split("-")
        self.check_version(version)

    def check_version(self, s):
        self.parse_version(s)

    def parse_version(self, s):
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
