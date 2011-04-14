##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import zope.interface
import zope.schema.interfaces
import zope.app.security.vocabulary

class ISimplePrincipalSource(zope.schema.interfaces.ISource):
    """Supports simple querying."""

class ISimpleUserSource(ISimplePrincipalSource):
    """Supports simple querying."""

class ISimpleGroupSource(ISimplePrincipalSource):
    """Supports simple querying."""


# XXX the search interfaces below should commit to searching by title, or
# have some other specified contract about sorting.

class ISimpleUserSearch(zope.interface.Interface):
    """Simple search limited to users
    """

    def searchUsers(filter, start, size):
        """Search for principals

        Return an iterable of principal ids.

        If a filter is supplied, principals are restricted to
        principals that "match" the filter string.  Typically,
        matching is based on subscrings of text such as principal
        titles, descriptions, etc.

        Results should be ordered in some consistent fashion, to make
        batching work in a reasonable way.

        No more than that number of
        principal ids will be returned.

        """

class ISimpleGroupSearch(zope.interface.Interface):
    """Simple search limited to users
    """

    def searchGroups(filter, start, size):
        """Search for principals

        Return an iterable of principal ids.

        If a filter is supplied, principals are restricted to
        principals that "match" the filter string.  Typically,
        matching is based on subscrings of text such as principal
        titles, descriptions, etc.

        Results should be ordered in some consistent fashion, to make
        batching work in a reasonable way.

        No more than that number of
        principal ids will be returned.

        """

class ISimplePrincipalSearch(zope.interface.Interface):
    """Simple search of all principals
    """

    def searchPrincipals(filter, start, size):
        """Search for principals

        Return an iterable of principal ids.

        If a filter is supplied, principals are restricted to
        principals that "match" the filter string.  Typically,
        matching is based on subscrings of text such as principal
        titles, descriptions, etc.

        Results should be ordered in some consistent fashion, to make
        batching work in a reasonable way.

        No more than that number of
        principal ids will be returned.

        """

