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
"""Support for handling dependency information."""

import re
import sets


_ident = "[a-zA-Z_][a-zA-Z_0-9]*"
_module_match = re.compile(r"%s(\.%s)*$" % (_ident, _ident)).match


def isModuleName(string):
    return _module_match(string) is not None


def load(f):
    deps = DependencyInfo()
    deps.load(f)
    return deps


class DependencyInfo(object):
    """Dependency information."""

    def __init__(self):
        self.packages = sets.Set()
        self.others = sets.Set()

    def load(self, f):
        while True:
            line = f.readline().strip()
            if not line:
                return
            if line[0] == "#":
                continue
            if isModuleName(line):
                self.packages.add(line)
            else:
                self.others.add(line)
