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
"""Basic dependency representation.

$Id$
"""


class Dependency(object):
    """Object representing a dependency."""

    def __init__(self, name, file, lineno):
        """Initialize a Dependency instance.

        name -- dotted name of the module

        file -- full path of a source file that depends on the module
        named by `name`

        lineno -- line number within file where the dependency was
        identified (import or ZCML reference)

        """
        self.name = name
        self.occurences = [(file, lineno)]

    def addOccurence(self, file, lineno):
        """Add occurenace of the dependency in the code."""
        self.occurences.append((file, lineno))

    def isSubPackageOf(self, dep):
        """Return True if this dependency's module is a sub-package of dep."""
        return self.name.startswith(dep.name + ".")

    def __cmp__(self, other):
        """Compare dependecies by module name."""
        return cmp(self.name, other.name)
