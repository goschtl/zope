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
__docformat__ = 'restructuredtext'

from zope.interface import Interface


class IFSSyncUtility(Interface):
    """Lookup file-system representation adapters."""

    def getSynchronizer(object):
        """Return an object that implements `IObjectEntry` for the argument.

        The return value may be:

        - An `IDirectoryEntry` adapter for the object is returned if the
          object is represented as a directory on the file system.

        - An `IFileEntry` adapter for the object is returned if the
          object is represented as a file on the file system.

        or

        - Default, if no synchronizser has been registered.
        """


class IGlobalFSSyncUtility(IFSSyncUtility):
    """Global registry for file-system representation adapters."""

    def provideSynchronizer(class_, factory):
        """Register a synchronizer.

        A factory for a Synchronization Adapter is provided to create
        synchronizers for instances of the class.
        """
