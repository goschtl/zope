##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interfaces to do with traversing.

$Id: traversing.py,v 1.1 2002/12/28 14:13:24 stevea Exp $
"""

from zope.interface import Interface

class IContainmentRoot(Interface):
    """Marker interface to designate root objects
    """

class INamespaceHandler(Interface):

    def __call__(name, parameters, pname, object, request):
        """Access a name in a namespace

        The name lookup usually depends on an object and/or a
        request. If an object or request is unavailable, None will be passed.

        The parameters provided, are passed as a sequence of
        name, value items.  The 'pname' argument has the original name
        before parameters were removed.

        It is not the respoonsibility of the handler to wrap the return value.
        """

class IObjectName(Interface):

    def __str__():
        """Get a human-readable string representation
        """

    def __repr__():
        """Get a string representation
        """

    def __call__():
        """Get a string representation
        """

class IPhysicallyLocatable(Interface):
    """Objects that have a physical location in a containment hierarchy.
    """

    def getPhysicalRoot():
        """Return the physical root object
        """

    def getPhysicalPath():
        """Return the physical path to the object as a sequence of names.
        """

class ITraversable(Interface):
    """To traverse an object, this interface must be provided"""

    def traverse(name, parameters, pname, furtherPath):
        """Get the next item on the path

        Should return the item corresponding to 'name' or raise
        NotFoundError where appropriate.

        The parameters provided, are passed as a sequence of
        name, value items.  The 'pname' argument has the original name
        before parameters were removed.

        furtherPath is a list of names still to be traversed. This method is
        allowed to change the contents of furtherPath.

        """

_RAISE_KEYERROR = object()

class ITraverser(Interface):
    """Provide traverse features"""

    def traverse(path, default=_RAISE_KEYERROR):
        """
        Return an object given a path.

        Path is either an immutable sequence of strings or a slash ('/')
        delimited string.

        If the first string in the path sequence is an empty string,
        or the path begins with a '/', start at the root. Otherwise the path
        is relative to the current context.

        If the object is not found, return 'default' argument.
        """
 
