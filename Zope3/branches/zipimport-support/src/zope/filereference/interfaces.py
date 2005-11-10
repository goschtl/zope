##############################################################################
#
# Copyright (c) 2001, 2002, 2003 Zope Corporation and Contributors.
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
"""Interfaces for zope.filereference.

"""
__docformat__ = "reStructuredText"

import zope.interface


class IFileReference(zope.interface.Interface):
    """Interface of a file reference object.

    File refereneces must also be strings.

    """

    def open(mode="r"):
        """Open the referenced resource, returning a file-like object.

        Only 'read' modes are supported.

        """

    def exists():
        """Returns True iff the resource exists."""

    def isdir():
        """Returns True iff the resource exists and is a directory."""

    def isfile():
        """Returns True iff the resource exists and is a file."""

    def getmtime():
        """Return the last-modified time for the file, or 0 if unavailable."""


class IFileReferenceAPI(zope.interface.Interface):
    """Interface for the general API for working with file references.

    The `ref` arguments for these functions may be paths as strings or
    `IFileReference` implementations.

    """

    def new(path, package=None, basepath=None):
        """Return a new `IFileReference` object."""

    def open(ref, mode="r"):
        """Open the referenced resource, returning a file-like object.

        Only 'read' modes are supported.

        """

    def exists(ref):
        """Returns True iff the resource exists."""

    def isdir(ref):
        """Returns True iff the resource exists and is a directory."""

    def isfile(ref):
        """Returns True iff the resource exists and is a file."""

    def getmtime(ref):
        """Return the last-modified time for the file, or 0 if unavailable."""
