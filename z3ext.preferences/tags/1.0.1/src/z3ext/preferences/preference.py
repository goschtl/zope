##############################################################################
#
# Copyright (c) 2007 Zope Corporation and Contributors.
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
"""

$Id$
"""
from BTrees.OOBTree import OOBTree

from zope import interface
from zope.interface.common.mapping import IEnumerableMapping
from zope.component import getGlobalSiteManager
from zope.component import queryUtility, getMultiAdapter
from zope.cachedescriptors.property import Lazy
from zope.security.management import getInteraction
from zope.annotation.interfaces import IAnnotations
from zope.app.component.hooks import getSite
from zope.app.security.interfaces import IAuthentication, PrincipalLookupError

from interfaces import IPreferenceGroup, IBound, UnboundPreferenceGroup

pref_key = 'zope.app.user.UserPreferences'

_marker = object()


class PreferenceGroup(object):
    interface.implements(IPreferenceGroup, IEnumerableMapping)

    __principal__ = None

    def __init__(self, tests=()):
        self.__name__ = self.__id__.rsplit('.', 1)[-1]
        self.__tests__ = tests
        self.__subgroups__ = ()

    def __bind__(self, parent=None, principal=None):
        clone = self.__class__.__new__(self.__class__)
        clone.__dict__.update(self.__dict__)

        if parent is None:
            parent = getSite()

        clone.__parent__ = parent

        if principal is None:
            if IBound.providedBy(parent):
                clone.__principal__ = parent.__principal__
            else:
                principal = getInteraction().participations[0].principal

                auth = queryUtility(IAuthentication)
                if auth is not None:
                    try:
                        principal = auth.getPrincipal(principal.id)
                    except PrincipalLookupError:
                        pass

                clone.__principal__ = principal
        else:
            clone.__principal__ = principal

        interface.alsoProvides(clone, IBound)
        return clone

    @Lazy
    def data(self):
        if not IBound.providedBy(self):
            raise UnboundPreferenceGroup()

        ann = getMultiAdapter((self.__principal__, self), IAnnotations)

        # If no preferences exist, create the root preferences object.
        if  ann.get(pref_key) is None:
            ann[pref_key] = OOBTree()
        prefs = ann[pref_key]

        # If no entry for the group exists, create a new entry.
        if self.__id__ not in prefs.keys():
            prefs[self.__id__] = OOBTree()

        return prefs[self.__id__]

    def isAvailable(self):
        if IPreferenceGroup.providedBy(self.__parent__):
            if not self.__parent__.isAvailable():
                return False

        for test in self.__tests__:
            if callable(test):
                if not test(self):
                    return False
            elif not bool(test):
                return False

        return True

    def add(self, name):
        if name not in self.__subgroups__:
            self.__subgroups__ = self.__subgroups__ + (name,)

            id = self.__id__
            if id:
                id = id + '.'

            items = []
            for grp_id in self.__subgroups__:
                name = id + grp_id

                group = queryUtility(IPreferenceGroup, name)
                if group is None:
                    group = getGlobalSiteManager().queryUtility(
                        IPreferenceGroup, name)

                if group is not None:
                    items.append((group.order, group.__title__, grp_id))

            items.sort()
            self.__subgroups__ = tuple([id for o,t,id in items])

    def remove(self, name):
        if name in self.__subgroups__:
            names = list(self.__subgroups__)
            names.remove(name)
            self.__subgroups__ = tuple(names)

    def get(self, key, default=None):
        id = self.__id__ and self.__id__ + '.' + key or key
        group = queryUtility(IPreferenceGroup, id, default)
        if group is default:
            return default
        return group.__bind__(self)

    def items(self):
        id = self.__id__
        if id:
            id = id + '.'

        items = []
        for key in self.keys():
            name = id + key
            group = queryUtility(IPreferenceGroup, name)
            if group is not None:
                items.append((name, group.__bind__(self)))
        return items

    def __getitem__(self, key):
        obj = self.get(key, _marker)
        if obj is _marker:
            raise KeyError(key)
        return obj

    def __contains__(self, key):
        return key in self.keys()

    def keys(self):
        return self.__subgroups__

    def __iter__(self):
        id = self.__id__
        if id:
            id = id + '.'

        for key in self.keys():
            name = id + key
            group = queryUtility(IPreferenceGroup, name)
            if group is not None:
                yield group.__bind__(self)

    def values(self):
        return [group for id, group in self.items()]

    def __len__(self):
        return len(self.keys())
