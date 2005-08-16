##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
""" Generic two-dimensional array type """

from persistent import Persistent
from persistent.dict import PersistentDict
from zope.interface import implements
from zope.app.securitypolicy.interfaces import ISecurityMap

class SecurityMap(object):

    implements(ISecurityMap)

    def __init__(self):
        self._clear()

    def _clear(self):
        self._byrow = {}
        self._bycol = {}

    def _empty_mapping(self):
        return {}

    def addCell(self, rowentry, colentry, value):
        # setdefault may get expensive if an empty mapping is
        # expensive to create, for PersistentDict for instance.
        row = self._byrow.setdefault(rowentry, self._empty_mapping())
        row[colentry] = value

        col = self._bycol.setdefault(colentry, self._empty_mapping())
        col[rowentry] = value

    def delCell(self, rowentry, colentry):
        row = self._byrow.get(rowentry)
        if row and (colentry in row):
            del self._byrow[rowentry][colentry]
            del self._bycol[colentry][rowentry]

    def getCell(self, rowentry, colentry, default=None):
        " return the value of a cell by row, entry "
        row = self._byrow.get(rowentry)
        if row: return row.get(colentry, default)
        else: return default

    def getRow(self, rowentry):
        " return a list of (colentry, value) tuples from a row "
        row = self._byrow.get(rowentry)
        if row:
            return row.items()
        else: return []

    def getCol(self, colentry):
        " return a list of (rowentry, value) tuples from a col "
        col = self._bycol.get(colentry)
        if col:
            return col.items()
        else: return []

    def getAllCells(self):
        " return a list of (rowentry, colentry, value) "
        res = []
        for r in self._byrow.keys():
            for c in self._byrow[r].items():
                res.append((r,) + c)
        return res


class PersistentSecurityMap(SecurityMap, Persistent):

    implements(ISecurityMap)

    def _clear(self):
        self._byrow = PersistentDict()
        self._bycol = PersistentDict()

    def _empty_mapping(self):
        return PersistentDict()
