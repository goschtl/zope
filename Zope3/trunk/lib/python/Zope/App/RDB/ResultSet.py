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
$Id: ResultSet.py,v 1.4 2002/12/02 20:03:49 alga Exp $
"""
from IResultSet import IResultSet
from Row import RowClassFactory

class ResultSet(list):
    """Database Result Set.

    Currently we don't do lazy instantation of rows.
    """

    __implements__ = IResultSet
    __slots__ = ('columns',)

    def __init__(self, columns, rows):
        self.columns = tuple(columns)
        row_class = RowClassFactory(columns)
        super(ResultSet, self).__init__(map(row_class, rows))

    def __setstate__(self, data):
        self.columns, rows = data
        row_class = RowClassFactory(self.columns)
        self.extend(map(row_class, rows))

    __safe_for_unpickling__ = True

    def __reduce__(self):
        cols = self.columns
        return (ResultSet, None,
                (self.columns,
                 [[getattr(row, col) for col in cols]
                  for row in self]
                ))

    def __basicnew__():
        return ResultSet((), ())
    __basicnew__ = staticmethod(__basicnew__)

    def __cmp__(self, other):
        if not isinstance(other, ResultSet):
            return super(ResultSet, self).__cmp__(other)
        c = cmp(self.columns, other.columns)
        if c:
            return c
        for row, other_row in zip(self, other):
            c = cmp(row, other_row)
            if c:
                return c
        return cmp(len(self), len(other))



