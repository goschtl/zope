##############################################################################
#
# Copyright (c) 2003 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Pluggable authentication adapters

$Id$
"""

from zc.security import interfaces
from zope.app.component import queryNextUtility
from zope.app.security import principalregistry
from zope.app.security.interfaces import IAuthentication
from zope.app.security.interfaces import PrincipalLookupError
from zope.security.interfaces import IGroup
import zope.app.authentication.authentication
import zope.app.authentication.groupfolder
import zope.app.authentication.interfaces
import zope.app.authentication.principalfolder
import zope.component
import zope.interface


class PASimpleSearch:

    zope.component.adapts(
        zope.app.authentication.interfaces.IPluggableAuthentication)

    def __init__(self, context):
        self.context = context

    def searchPrincipals(self, filter, start, size):
        if size <= 0:
            return

        prefix = self.context.prefix

        n = 0
        for name, plugin in self.context.getAuthenticatorPlugins():
            searcher = self.type(plugin, None)
            if searcher is None:
                continue

            sz = size + start - n
            if sz <= 0:
                return

            search = getattr(searcher, self.meth)
            for principal_id in search(filter, 0, sz):
                if n >= start:
                    yield prefix + principal_id
                n += 1

        next = self.context
        while 1:
            next = queryNextUtility(next, IAuthentication)
            if next is None:
                return
            searcher = self.type(next, None)
            if searcher is None:
                continue

            sz = size + start - n
            if sz <= 0:
                return

            search = getattr(searcher, self.meth)
            for principal_id in search(filter, 0, sz):
                if n >= start:
                    yield principal_id
                n += 1
            return


class PASimpleGroupSearch(PASimpleSearch):
    type = interfaces.ISimpleGroupSearch
    zope.interface.implements(type)
    meth = 'searchGroups'
    searchGroups = PASimpleSearch.searchPrincipals

class PASimpleUserSearch(PASimpleSearch):
    type = interfaces.ISimpleUserSearch
    zope.interface.implements(type)
    meth = 'searchUsers'
    searchUsers = PASimpleSearch.searchPrincipals

class GroupFolderSimpleGroupSearch:

    def __init__(self, context):
        self.context = context

    def searchGroups(self, filter, start, size):
        return self.context.search({'search': filter}, start, size)

    zope.component.adapts(zope.app.authentication.groupfolder.IGroupFolder)
    zope.interface.implements(interfaces.ISimpleGroupSearch)

class UserFolderSimpleUserSearch:

    zope.component.adapts(
        zope.app.authentication.principalfolder.PrincipalFolder)
    zope.interface.implements(interfaces.ISimpleUserSearch)

    def __init__(self, context):
        self.context = context

    def searchUsers(self, filter, start, size):
        return self.context.search({'search': filter}, start, size)

class UserRegistrySimpleUserSearch:

    zope.component.adapts(principalregistry.PrincipalRegistry)
    zope.interface.implements(interfaces.ISimpleUserSearch)

    def __init__(self, context):
        self.context = context

    def searchUsers(self, filter, start, size):
        filter = filter.lower()
        result = [p.id for p in list(self.context.getPrincipals(''))
                  if (filter in p.getLogin().lower()
                      or
                      filter in p.title.lower()
                      or
                      filter in p.description.lower()
                      ) and not IGroup.providedBy(p)]
        result.sort()
        return result[start:start+size]

class UserRegistrySimpleGroupSearch(UserRegistrySimpleUserSearch):
    zope.interface.implementsOnly(interfaces.ISimpleGroupSearch)

    def searchGroups(self, filter, start, size):
        filter = filter.lower()
        result = [p.id for p in list(self.context.getPrincipals(''))
                  if (filter in p.getLogin().lower()
                      or
                      filter in p.title.lower()
                      or
                      filter in p.description.lower()
                      ) and IGroup.providedBy(p)]
        result.sort()
        return result[start:start+size]

class SimplePrincipalSource(zope.app.security.vocabulary.PrincipalSource):
    zope.interface.implementsOnly(interfaces.ISimplePrincipalSource)

class SimpleUserSource(zope.app.security.vocabulary.PrincipalSource):
    zope.interface.implementsOnly(interfaces.ISimpleUserSource)

    def __contains__(self, id):
        auth = zope.component.getUtility(IAuthentication)
        try:
            return not IGroup.providedBy(auth.getPrincipal(id))
        except PrincipalLookupError:
            return False

class SimpleGroupSource(zope.app.security.vocabulary.PrincipalSource):
    zope.interface.implementsOnly(interfaces.ISimpleGroupSource)

    def __contains__(self, id):
        auth = zope.component.getUtility(IAuthentication)
        try:
            return IGroup.providedBy(auth.getPrincipal(id))
        except PrincipalLookupError:
            return False

class SimplePrincipalSearch:

    zope.interface.implements(interfaces.ISimplePrincipalSearch)
    zope.component.adapts(IAuthentication)

    def __init__(self, context):
        self.context = context

    def searchPrincipals(self, filter, start, size):
        count = 0

        user_search = interfaces.ISimpleUserSearch(self.context, None)
        if user_search is not None:
            users = user_search.searchUsers(filter, 0, size+start)
            for user in users:
                if count >= start:
                    yield user
                count += 1

            if count-start == size:
                return

        group_search = interfaces.ISimpleGroupSearch(self.context, None)
        if group_search is not None:
            groups = group_search.searchGroups(filter, 0, size+start-count)
            for group in groups:
                if count >= start:
                    yield group
                count += 1

            if count-start == size:
                return
