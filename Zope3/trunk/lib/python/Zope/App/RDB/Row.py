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

$Id: Row.py,v 1.1 2002/06/25 15:41:45 k_vertigo Exp $
"""
from Zope.Security import Checker

class row(object):

    def __init__(self, data):
        for k, v in zip(self.__slots__, data):
            setattr(self, k, v)

def row_class_factory(columns):

    klass_namespace = {}
    
    klass_namespace['__Security_checker__']=Checker.NamesChecker(columns)
    klass_namespace['__slots__']=tuple(columns)

    return type('row class', (row,), klass_namespace)



