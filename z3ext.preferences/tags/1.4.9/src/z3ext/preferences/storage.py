##############################################################################
#
# Copyright (c) 2008 Zope Corporation and Contributors.
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

from zope import interface, component
from zope.security.interfaces import IPrincipal
from zope.annotation.interfaces import IAnnotations

from interfaces import ANNOTATION_KEY, IDataStorage, IPreferenceGroup


@interface.implementer(IDataStorage)
@component.adapter(IPrincipal, IPreferenceGroup)
def getDefaultStorage(principal, preference):
    ann = IAnnotations(principal)

    # If no preferences exist, create the root preferences object.
    if  ann.get(ANNOTATION_KEY) is None:
        ann[ANNOTATION_KEY] = OOBTree()
    prefs = ann[ANNOTATION_KEY]

    # If no entry for the group exists, create a new entry.
    id = preference.__schema__.getTaggedValue('preferenceID')
    if id not in prefs:
        prefs[id] = OOBTree()

    return DataStorage(prefs[id], preference.__schema__)


class DataStorage(object):
    interface.implements(IDataStorage)

    def __init__(self, btree, schema):
        self.__dict__['__btree__'] = btree
        self.__dict__['__schema__'] = schema

    def __getattr__(self, attr):
        if attr in self.__btree__:
            return self.__btree__[attr]
        else:
            raise AttributeError(attr)

    def __setattr__(self, attr, value):
        self.__btree__[attr] = value

    def __delattr__(self, attr):
        if attr in self.__btree__:
            del self.__btree__[attr]
