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
"""Security map to hold matrix-like relationships.

$Id: securitymap.py,v 1.1 2004/03/08 12:07:34 srichter Exp $
"""
from zope.interface import Interface


class ISecurityMap(Interface):
    """Security map to hold matrix-like relationships."""

    def addCell(rowentry, colentry, value):
        " add a cell "

    def delCell(rowentry, colentry):
        " delete a cell "

    # XXX queryCell / getCell ?
    def getCell(rowentry, colentry, default=None):
        " return the value of a cell by row, entry "

    def getRow(rowentry):
        " return a list of (colentry, value) tuples from a row "

    def getCol(colentry):
        " return a list of (rowentry, value) tuples from a col "

    def getAllCells():
        " return a list of (rowentry, colentry, value) "
