##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces for filesystem synchronization.

$Id$
"""

from zope.interface import Interface


class IObjectEntry(Interface):
    """File-system object representation."""

    def extra():
        """Return extra data for the entry.

        The data are returned as a mapping object that allows *both*
        data retrieval and setting.  The mapping is from names to
        objects that will be serialized to or from the file system.
        """

    def typeIdentifier():
        """Return a dotted name that identifies the object type.

        This is typically a dotted class name.

        This is used when synchronizing from the file system to the
        database to decide whether the existing object and the new
        object are of the same type.
        """

    def factory():
        """Return the dotted name of a factory to recreate an empty entry.

        The factory will be called with no arguments. It is usually
        the dotted name of the object class.
        """


class IObjectFile(IObjectEntry):
    """File-system object representation for file-like objects."""

    def getBody():
        """Return the file body."""

    def setBody(body):
        """Change the file body."""


class IObjectDirectory(IObjectEntry):
    """File-system object representation for directory-like objects."""

    def contents():
        """Return the contents.

        A sequence of name, value object are returned. The value in each
        pair will be syncronized.
        """


class IContentDirectory(IObjectDirectory):
    """Marker interface for synchronization of content containers.

    Any container type object should implement this interface
    verifying if the objects are of container types.
    """
