##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Interfaces for filesystem synchronization.

$Id: fssync.py,v 1.2 2003/05/05 18:01:02 gvanrossum Exp $
"""

from zope.component.interfaces import IView
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


class IFSSyncService(Interface):
    """Lookup file-system representation adapters."""

    def getSynchronizer(object):
        """Return an object that implements IObjectEntry for the argument.

        The return value may be:

        - An IDirectoryEntry adapter for the object is returned if the
          object is represented as a directory on the file system.

        - An IFileEntry adapter for the object is returned if the
          object is represented as a file on the file system.

        or

        - Default, if no synchronizser has been registered.
        """


class IGlobalFSSyncService(IFSSyncService):
    """Global registry for file-system representation adapters."""

    def provideSynchronizer(class_, factory):
        """Register a synchronizer.

        A factory for a Synchronization Adapter is provided to create
        synchronizers for instances of the class.
        """


class IFSAddView(IView):
    """Add objects to ZODB from file system.

    Implementation of this view helps in creating
    file system representation for zope objects.
    """

    def create(fspath=None):
        """Create file system representation for zope objects."""
