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
"""
$Id: configurationmanager.py,v 1.3 2003/02/03 14:53:38 jim Exp $
"""

__metaclass__ = type

from persistence import Persistent
from zope.app.interfaces.services.configurationmanager \
     import IConfigurationManager
from zope.app.interfaces.container import IDeleteNotifiable
from zope.app.interfaces.container import IZopeWriteContainer
from zope.component import getAdapter


class ConfigurationManager(Persistent):
    """Configuration manager

    Manages configurations within a package.
    """

    __implements__ = IConfigurationManager, IDeleteNotifiable

    def __init__(self):
        self._data = ()
        self._next = 0

    def __getitem__(self, key):
        "See IItemContainer"
        v = self.get(key)
        if v is None:
            raise KeyError, key
        return v

    def get(self, key, default=None):
        "See Interface.Common.Mapping.IReadMapping"
        for k, v in self._data:
            if k == key:
                return v
        return default

    def __contains__(self, key):
        "See Interface.Common.Mapping.IReadMapping"
        return self.get(key) is not None


    def keys(self):
        "See Interface.Common.Mapping.IEnumerableMapping"
        return [k for k, v in self._data]

    def __iter__(self):
        return iter(self.keys())

    def values(self):
        "See Interface.Common.Mapping.IEnumerableMapping"
        return [v for k, v in self._data]

    def items(self):
        "See Interface.Common.Mapping.IEnumerableMapping"
        return self._data

    def __len__(self):
        "See Interface.Common.Mapping.IEnumerableMapping"
        return len(self._data)

    def setObject(self, key, object):
        "See IWriteContainer"
        self._next += 1
        key = str(self._next)
        self._data += ((key, object), )
        return key

    def __delitem__(self, key):
        "See IWriteContainer"
        if key not in self:
            raise KeyError, key
        self._data = tuple(
            [item
             for item in self._data
             if item[0] != key]
            )

    def moveTop(self, names):
        self._data = tuple(
            [item for item in self._data if (item[0] in names)]
            +
            [item for item in self._data if (item[0] not in names)]
            )

    def moveBottom(self, names):
        self._data = tuple(
            [item for item in self._data if (item[0] not in names)]
            +
            [item for item in self._data if (item[0] in names)]
            )

    def _moveUpOrDown(self, names, direction):
        # Move each named item by one position. Note that this
        # might require moving some unnamed objects by more than
        # one position.

        indexes = {}

        # Copy named items to positions one less than they currently have
        i = -1
        for item in self._data:
            i += 1
            if item[0] in names:
                j = max(i + direction, 0)
                while j in indexes:
                    j += 1

                indexes[j] = item

        # Fill in the rest where there's room.
        i = 0
        for item in self._data:
            if item[0] not in names:
                while i in indexes:
                    i += 1
                indexes[i] = item

        items = indexes.items()
        items.sort()

        self._data = tuple([item[1] for item in items])

    def moveUp(self, names):
        self._moveUpOrDown(names, -1)

    def moveDown(self, names):
        self._moveUpOrDown(names, 1)

    def manage_beforeDelete(self, object, container):
        assert object == self
        container = getAdapter(object, IZopeWriteContainer)
        for k, v in self._data:
            del container[k]


__doc__ = ConfigurationManager.__doc__  + __doc__
