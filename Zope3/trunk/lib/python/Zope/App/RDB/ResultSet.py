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
$Id: ResultSet.py,v 1.3 2002/07/10 23:37:26 srichter Exp $
"""
from Zope.App.RDB.IResultSet import IResultSet
 
class ResultSet(list):    
    """Database Result Set. 

    Currently we don't do lazy instantation of rows.
    """

    __implements__ = IResultSet
    __slots__ = ('names', 'row_klass')
    
    def __init__(self, names, data, row_klass):
        self.names = tuple(names)
        self.row_klass = row_klass
        super(ResultSet, self).__init__(map(row_klass, data))
    
