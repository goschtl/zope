##############################################################################
#
# Copyright (c) 2003-2009 Zope Corporation and Contributors.
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
"""Location framework interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.schema

_RAISE_KEYERROR = object()


class ILocation(zope.interface.Interface):
    """Objects that can be located in a hierachy.

    Given a parent and a name an object can be located within that parent. The
    locatable object's `__name__` and `__parent__` attributes store this
    information.

    Located objects form a hierarchy that can be used to build file-system-like
    structures. For example in Zope `ILocation` is used to build URLs and to
    support security machinery.

    To retrieve an object from its parent using its name, the `ISublocation`
    interface provides the `sublocations` method to iterate over all objects
    located within the parent. The object searched for can be found by reading
    each sublocation's __name__ attribute.

    """

    __parent__ = zope.interface.Attribute("The parent in the location hierarchy.")

    __name__ = zope.schema.TextLine(
        title=u"The name within the parent",
        description=u"The object can be looked up from the parent's "
            "sublocations using this name.",
        required=False,
        default=None)


class ILocationInfo(zope.interface.Interface):
    """Provides supplemental information for located objects.

    Requires that the object has been given a location in a hierarchy.

    """

    def getRoot():
        """Return the root object of the hierarchy."""

    def getPath():
        """Return the physical path to the object as a string.

        Uses '/' as the path segment separator.

        """

    def getName():
        """Return the last segment of the physical path."""

    def getNearestSite():
        """Return the site the object is contained in

        If the object is a site, the object itself is returned.

        """


class ISublocations(zope.interface.Interface):
    """Provide access to sublocations of an object.

    All objects with the same parent object are called the ``sublocations`` of
    that parent.

    """

    def sublocations():
        """Return an iterable of the object's sublocations."""


class IRoot(zope.interface.Interface):
    """Marker interface to designate root objects within a location hierarchy.
    """




class ITraverser(zope.interface.Interface):
    """Provide traverse features"""

    # XXX This is used like a utility but implemented as an adapter: The
    # traversal policy is only implemented once and repeated for all objects
    # along the path.

    def traverse(path, default=_RAISE_KEYERROR):
        """Return an object given a path.

        Path is either an immutable sequence of strings or a slash ('/')
        delimited string.

        If the first string in the path sequence is an empty string, or the
        path begins with a '/', start at the root. Otherwise the path is
        relative to the current context.

        If the object is not found, return 'default' argument.

        """


class LocationError(KeyError, LookupError):
    """There is no object for a given location."""


class IPossibleSite(zope.interface.Interface):
    """An object that could be a site.
    """

    def setSiteManager(sitemanager):
        """Sets the site manager for this object.
        """

    def getSiteManager():
        """Returns the site manager contained in this object.

        If there isn't a site manager, raise a component lookup.
        """


class ISite(IPossibleSite):
    """Marker interface to indicate that we have a site"""
