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

$Id: definition.py,v 1.8 2004/03/03 20:20:33 srichter Exp $
"""
from persistent import Persistent
from persistent.dict import PersistentDict

from zope.interface import implements

from zope.app.container.contained import Contained, setitem, uncontained
from zope.app.workflow.interfaces import IProcessDefinitionElementContainer
from zope.app.workflow.interfaces import IProcessDefinition

class ProcessDefinition(Persistent, Contained):
    """Abstract Process Definition class.

    Must be inherited by a particular implementation.
    """ 
    implements(IProcessDefinition)

    name = None

    def createProcessInstance(self, definition_name):
        """See zope.app.workflow.interfaces.IProcessDefinition"""
        return None


class ProcessDefinitionElementContainer(Persistent, Contained):
    """See IProcessDefinitionElementContainer"""
    implements(IProcessDefinitionElementContainer)

    def __init__(self):
        super(ProcessDefinitionElementContainer, self).__init__()
        self.__data = PersistentDict()

    def keys(self):
        """See IProcessDefinitionElementContainer"""
        return self.__data.keys()

    def __iter__(self):
        return iter(self.__data.keys())

    def __getitem__(self, name):
        """See IProcessDefinitionElementContainer"""
        return self.__data[name]

    def get(self, name, default=None):
        """See IProcessDefinitionElementContainer"""
        return self.__data.get(name, default)

    def values(self):
        """See IProcessDefinitionElementContainer"""
        return self.__data.values()

    def __len__(self):
        """See IProcessDefinitionElementContainer"""
        return len(self.__data)

    def items(self):
        """See IProcessDefinitionElementContainer"""
        return self.__data.items()

    def __contains__(self, name):
        """See IProcessDefinitionElementContainer"""
        return name in self.__data

    has_key = __contains__

    def __setitem__(self, name, object):
        """See IProcessDefinitionElementContainer"""
        setitem(self, self.__data.__setitem__, name, object)

    def __delitem__(self, name):
        """See IProcessDefinitionElementContainer"""
        uncontained(self.__data[name], self, name)
        del self.__data[name]

    def getProcessDefinition(self):
        return self.__parent__
