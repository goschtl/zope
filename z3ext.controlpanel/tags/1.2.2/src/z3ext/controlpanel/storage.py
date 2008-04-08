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

from zope import interface
from zope.app.component.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from z3ext.controlpanel.interfaces import IDataStorage

key = 'z3ext.controlpanel.Settings'
_temp = {}

class DataStorage(object):
    interface.implements(IDataStorage)

    @property
    def _data(self):
        site = getSite()
        ann = IAnnotations(site, None)
        if ann is None:
            return _temp

        storage = ann.get(key)
        if storage is None:
            storage = OOBTree()
            ann[key] = storage

        return storage

    def __getitem__(self, name):
        try:
            return self._data[name]
        except KeyError:
            self._data[name] = OOBTree()
            return self._data[name]
