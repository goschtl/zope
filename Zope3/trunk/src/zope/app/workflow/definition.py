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
"""Implementation of workflow process definition.

$Id: definition.py,v 1.1 2003/05/08 17:27:18 jack-e Exp $
"""
__metaclass__ = type

from types import StringTypes
from persistence import Persistent
from persistence.dict import PersistentDict
from zope.proxy.context import ContextAware, getWrapperContainer
from zope.app.interfaces.workflow \
     import IProcessDefinition, IProcessDefinitionElementContainer


class ProcessDefinition(Persistent):

    __doc__ = IProcessDefinition.__doc__
    
    __implements__ = IProcessDefinition

    name = None

    ############################################################
    # Implementation methods for interface
    # zope.app.interfaces.workflow.IProcessDefinition

    def createProcessInstance(self, definition_name):
        return None

    #
    ############################################################





class ProcessDefinitionElementContainer(ContextAware, Persistent):
    """ See IProcessDefinitionElementContainer.
    """

    __implements__ = IProcessDefinitionElementContainer

    def __init__(self):
        super(ProcessDefinitionElementContainer, self).__init__()
        self.__data = PersistentDict()

    def keys(self):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.keys()
 
    def __iter__(self):
        return iter(self.__data.keys())
 
    def __getitem__(self, key):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data[key]
 
    def get(self, key, default=None):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.get(key, default)
 
    def values(self):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.values()
 
    def __len__(self):
        '''See interface IProcessDefinitionElementContainer'''
        return len(self.__data)
 
    def items(self):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.items()
 
    def __contains__(self, key):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.has_key(key)
 
    has_key = __contains__
 
    def setObject(self, key, object):
        '''See interface IProcessDefinitionElementContainer'''
        bad = False
        if isinstance(key, StringTypes):
            try:
                unicode(key)
            except UnicodeError:
                bad = True
        else:
            bad = True
        if bad:
            raise TypeError("'%s' is invalid, the key must be an "
                            "ascii or unicode string" % key)
        if len(key) == 0:
            raise ValueError("The key cannot be an empty string")
        self.__data[key] = object
        return key
                
    def __delitem__(self, key):
        '''See interface IProcessDefinitionElementContainer'''
        del self.__data[key]


    def getProcessDefinition(self):
        return getWrapperContainer(self)
