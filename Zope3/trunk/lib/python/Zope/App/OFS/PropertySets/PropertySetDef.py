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
from Zope.App.OFS.PropertySets.IPropertySetDef import IPropertySetDef
from Zope.Exceptions import DuplicationError

class PropertySetDef:

    __implements__ =  IPropertySetDef

    ############################################################
    # Implementation methods for interface
    # Zope.App.OFS.PropertySets.IPropertySetDef.

    def __init__(self):
        '''See interface IPropertySetDef'''
        self.fields = {}

    def has_field(self, name):
        '''See interface IPropertySetDef'''
        return name in self.fields

    def addField(self, name, field):
        '''See interface IPropertySetDef'''
        if name in self.fields:
            raise DuplicationError(name)
        self.fields[name] = field

    def getField(self, name):
        '''See interface IPropertySetDef'''
        return self.fields[name]

    def fieldNames(self):
        '''See interface IPropertySetDef'''
        return self.fields.keys()

    def __len__(self):
        '''See interface IPropertySetDef'''
        return len(self.fields)

    def __iter__(self):
        '''See interface IPropertySetDef'''
        return self.fields.itervalues()

    #
    ############################################################
