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
$Id: Row.py,v 1.4 2002/12/02 20:03:49 alga Exp $
"""
from Zope.Security import Checker

class Row(object):
    """Represents a row in a ResultSet"""

    def __init__(self, data):
        for k, v in zip(self.__slots__, data):
            setattr(self, k, v)

    def __str__(self):
        return "row class %s" % str(self.__slots__)

    def __cmp__(self, other):
        if not isinstance(other, Row):
            return super(Row, self).__cmp__(other)
        c = cmp(self.__slots__, other.__slots__)
        if c:
            return c
        for column in self.__slots__:
            c = cmp(getattr(self, column), getattr(other, column))
            if c:
                return c
        return 0

def RowClassFactory(columns):
    """Creates a Row object"""
    klass_namespace = {}

    klass_namespace['__Security_checker__'] = Checker.NamesChecker(columns)
    klass_namespace['__slots__'] = tuple(columns)

    return type('GeneratedRowClass', (Row,), klass_namespace)

