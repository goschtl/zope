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
"""XXX short summary goes here.

XXX longer description goes here.

$Id: ResultSet.py,v 1.2 2002/07/01 14:40:04 k_vertigo Exp $
"""
 
class ResultSet(list):    
    """
    Database Result Set. 

    currently we don't do lazy instantation of rows.
    """
    
    __slots__ = ('names', 'row_klass')
    
    def __init__(self, names, data, row_klass):
        self.names = tuple(names)
        self.row_klass = row_klass
        super(ResultSet, self).__init__(map(row_klass, data))
    
