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
$Id: Row.py,v 1.3 2002/07/10 23:37:26 srichter Exp $
"""
from Zope.Security import Checker

class Row(object):
    """Represents a row in a ResultSet"""
    
    def __init__(self, data):
        for k, v in zip(self.__slots__, data):
            setattr(self, k, v)

    def __str__(self):
        return "row class %s"%str(self.__slots__)

            
def RowClassFactory(columns):
    """Creates a Row object"""
    klass_namespace = {}
    
    klass_namespace['__Security_checker__'] = Checker.NamesChecker(columns)
    klass_namespace['__slots__'] = tuple(columns)

    return type('row class', (Row,), klass_namespace)



