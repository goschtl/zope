##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Implementation of workflow process definition.

$Id$
"""
from persistent import Persistent
from persistent.dict import PersistentDict

from zope.interface import implements

from zope.schema.interfaces import ITokenizedTerm
from zope.schema.interfaces import IVocabularyTokenized

from zope.app import zapi
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


class ProcessDefinitionTerm(object):
    """A term representing the name of a process definition."""
    implements(ITokenizedTerm)

    def __init__(self, name):
        self.value = self.token = name


class ProcessDefinitionVocabulary(object):
    """Vocabulary providing available process definition names."""
    implements(IVocabularyTokenized)

    def __init__(self, context):
        self.sm = zapi.getSiteManager(context)

    def __names(self):
        return [name
                for name, util in self.sm.getUtilitiesFor(IProcessDefinition)]

    def __contains__(self, value):
        """See zope.schema.interfaces.IVocabulary"""
        return value in self.__names()

    def __iter__(self):
        """See zope.schema.interfaces.IVocabulary"""
        terms = [ProcessDefinitionTerm(name) for name in self.__names()]
        return iter(terms)

    def __len__(self):
        """See zope.schema.interfaces.IVocabulary"""
        return len(self.__names())

    def getTerm(self, value):
        """See zope.schema.interfaces.IVocabulary"""
        return ProcessDefinitionTerm(value)

    def getTermByToken(self, token):
        """See zope.schema.interfaces.IVocabularyTokenized"""
        return self.getTerm(token)
