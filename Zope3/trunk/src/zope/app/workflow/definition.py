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

$Id: definition.py,v 1.6 2004/02/27 16:50:37 philikon Exp $
"""
__metaclass__ = type

from types import StringTypes
from persistent import Persistent
from persistent.dict import PersistentDict
from zope.app.workflow.interfaces import IProcessDefinitionElementContainer
from zope.app.workflow.interfaces import IProcessDefinition
from zope.interface import implements
from zope.app.container.contained import Contained, setitem, uncontained

class ProcessDefinition(Persistent, Contained):
    __doc__ = IProcessDefinition.__doc__

    implements(IProcessDefinition)

    name = None

    def createProcessInstance(self, definition_name):
        """See zope.app.workflow.interfaces.IProcessDefinition"""
        return None

class ProcessDefinitionElementContainer(Persistent, Contained):
    """ See IProcessDefinitionElementContainer.
    """
    implements(IProcessDefinitionElementContainer)

    def __init__(self):
        super(ProcessDefinitionElementContainer, self).__init__()
        self.__data = PersistentDict()

    def keys(self):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.keys()

    def __iter__(self):
        return iter(self.__data.keys())

    def __getitem__(self, name):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data[name]

    def get(self, name, default=None):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.get(name, default)

    def values(self):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.values()

    def __len__(self):
        '''See interface IProcessDefinitionElementContainer'''
        return len(self.__data)

    def items(self):
        '''See interface IProcessDefinitionElementContainer'''
        return self.__data.items()

    def __contains__(self, name):
        '''See interface IProcessDefinitionElementContainer'''
        return name in self.__data

    has_key = __contains__

    def __setitem__(self, name, object):
        '''See interface IProcessDefinitionElementContainer'''
        setitem(self, self.__data.__setitem__, name, object)

    def __delitem__(self, name):
        '''See interface IProcessDefinitionElementContainer'''
        uncontained(self.__data[name], self, name)
        del self.__data[name]

    def getProcessDefinition(self):
        return self.__parent__
