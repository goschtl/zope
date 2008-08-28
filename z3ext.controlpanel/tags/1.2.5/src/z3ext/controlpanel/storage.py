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
""" IDataStorage implementation

$Id$
"""
from BTrees.OOBTree import OOBTree

from zope import interface, component, event
from zope.proxy import removeAllProxies
from zope.location.pickling import locationCopy
from zope.location.interfaces import ILocation
from zope.app.component.hooks import getSite
from zope.app.component.interfaces import ISite
from zope.annotation.interfaces import IAnnotations
from zope.lifecycleevent import ObjectCopiedEvent
from zope.lifecycleevent.interfaces import IObjectCopiedEvent
from z3ext.controlpanel.interfaces import IDataStorage

ANNOTATION_KEY = 'z3ext.controlpanel.Settings'
_temp = {}


class DataStorage(object):
    interface.implements(IDataStorage)

    @property
    def _data(self):
        site = getSite()
        ann = IAnnotations(site, None)
        if ann is None:
            return _temp

        storage = ann.get(ANNOTATION_KEY)
        if storage is None:
            storage = OOBTree()
            ann[ANNOTATION_KEY] = storage

        return storage

    def __getitem__(self, name):
        data = self._data.get(name)

        if data is None:
            data = OOBTree()
            self._data[name] = data

        return data

    def __setitem__(self, name, data):
        self._data[name] = data

    def __delitem__(self, name):
        if name in self._data:
            del self._data[name]

    def __contains__(self, name):
        return name in self._data


@component.adapter(ISite, IObjectCopiedEvent)
def dataStorageCopied(site, event):
    ann = IAnnotations(removeAllProxies(event.original), None)
    if ann is None:
        return

    oldStorage = ann.get(ANNOTATION_KEY)
    if oldStorage is None:
        return

    ann = IAnnotations(removeAllProxies(site), None)
    if ann is None:
        return

    newStorage = ann.get(ANNOTATION_KEY)
    if newStorage is None:
        newStorage = OOBTree()
        ann[key] = newStorage

    for key, obj in oldStorage.items():
        copy = locationCopy(obj)

        if isinstance(obj, OOBTree):
            for subkey, subobj in obj.items():
                subcopy = locationCopy(subobj)
                if ILocation.providedBy(obj):
                    subcopy.__parent__ = subcopy.__name__ = None
                    event.notify(ObjectCopiedEvent(subcopy, subobj))

                copy[subkey] = subcopy

        newStorage[key] = copy
