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
"""Generic symmetric one-to-many id map."""


class SecurityMap:
    def __init__(self):
        self._clear()

    def delCell(self, rowentry, colentry):
        row = self._byrow.get(rowentry, ())
        if colentry in row:
            row.remove(colentry)

        col = self._bycol.get(colentry, ())
        if rowentry in col:
            col.remove(rowentry)
            
    def addCell(self, rowentry, colentry):
        """Add a cell to the table."""
        row = self._byrow.get(rowentry)
        if row is None:
            self._byrow[rowentry] = [colentry]
        else:
            if colentry not in row:
                row.append(colentry)

        col = self._bycol.get(colentry)
        if col is None:
            self._bycol[colentry] = [rowentry]
        else:
            if rowentry not in col:
                col.append(rowentry)

    def getColumnsForRow(self, rowentry):
        """Return a list of column entries for a given row entry.

        If the row entry is not in the table, return an empty list.
        """
        return self._byrow.get(rowentry, [])

    def getRowsForColumn(self, colentry):
        """Return a list of row entries for a given column entry.

        If the column entry is not in the table, return an empty list.
        """
        return self._bycol.get(colentry, [])

    def _clear(self):
        self._byrow = {}
        self._bycol = {}        
