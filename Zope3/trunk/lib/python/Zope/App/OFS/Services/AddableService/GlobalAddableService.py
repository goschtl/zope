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
"""
generic AddableContentService

$Id: GlobalAddableService.py,v 1.2 2002/06/10 23:28:10 jim Exp $
"""
from Zope.ComponentArchitecture import getService, getFactoryInterfaces, \
     ComponentLookupError
from IAddableService import IAddableService
from Addable import Addable
from Zope.App.OFS.Container.IContainer import IWriteContainer
from Zope.App.OFS.Container.IContainer import IHomogenousContainer
from Zope.Proxy.ProxyIntrospection import removeAllProxies

class IGlobalAddableService(IAddableService):
    
    def provideAddable(self, id, title, description, for_container=None,
                       creation_markers=None):
        """adds addable to service, associated with id (used in
        factory service for the class)
        
        for_container is interface or interface tuple indicating type of
        container to which this addable can be added (any match in list
        is sufficient, including subclasses)
        
        creation_markers are marker interfaces to which one can associate
        views for this addable (for pre-creation views)
        
        raises DuplicateError if id is already used in this service"""

def multi_implement_check(interface, object):
    if type(interface) is tuple:
        for inter in interface:
            if multi_implement_check(inter, object):
                return 1
        return 0
    return interface.isImplementedBy(object)

class GlobalAddableService: # file system
    
    __implements__=IGlobalAddableService

    def provideAddable(self, id, title, description, for_container=None,
                       creation_markers=None):
        self.__reg.append(Addable(id, title, description, 
                                  for_container=for_container, 
                                  creation_markers=creation_markers))

    def getAddables(self, ob, allowed_types=None):
        clean_object=removeAllProxies(ob)
        addables=[]
        for addable in self.__reg:
            for_c=addable.for_container
            if not for_c or multi_implement_check(for_c, clean_object):

                try:
                    inter=getFactoryInterfaces(ob, addable.id)
                except ComponentLookupError:
                    continue
                if (IHomogenousContainer.isImplementedBy(clean_object)
                    and not
                    ob.isAddable(inter)
                    ):
                    continue

                addables.append(addable)
        return addables
    
    def _clear(self):
        self.__reg = []

    __init__ = _clear

addableContent=GlobalAddableService()
addableServices=GlobalAddableService()


def _clear():
    addableContent._clear()
    addableServices._clear()


# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
del addCleanUp
