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
from IZMIViewService import IZMIViewService
from Interface.Implements import objectImplements, flattenInterfaces
from Zope.Proxy.ContextWrapper import getWrapperContainer
from Zope.ComponentArchitecture import getAdapter
from Zope.App.Traversing.ITraverser import ITraverser
from Zope.Security.SecurityManagement import getSecurityManager
from Zope.Proxy.ProxyIntrospection import removeAllProxies
from Zope.App.PageTemplate.Engine import Engine
from Zope.Exceptions import Unauthorized


class ZMIViewService:
    
    __implements__ = IZMIViewService

    def __init__(self):
        self._reg = {}

    def _clear(self):
        """ for testing """
        self._reg = {}

    def registerView(self, interface, label, action, filter='python: 1'):
        """ register a zmi view """
        
        views = self._reg.get(interface, [])
        views.append( ZMIViewDescriptor(label, action, filter) )
        self._reg[interface]=views
 
    def getViews(self, object):
        """ see inteface docs. returns views in order defined
        with tabs from more general interfaces coming after
        more specific. """
        
        res = []
        
        obj_interfaces = flattenInterfaces(objectImplements(
            removeAllProxies(object)
            ))

        for interface in obj_interfaces:
            
            view_descriptors = self._reg.get(interface, ())

            adapter = getAdapter(object, ITraverser)
            
            for v in view_descriptors:
                
                view_value = (v.label, v.action)
                
                if view_value in res:
                    continue

                if v.filter is not None:
                    try:
                        include = v.filter(Engine.getContext(
                            context = object,
                            nothing = None))
                    except Unauthorized:
                        include = 0

                    if not include:
                        continue
                    
                res.append( view_value )
                
        return res

class ZMIViewDescriptor:

    def __init__(self, label, action, filter_string):
        self.label = label
        self.action = action
        if filter_string:
            self.filter = Engine.compile(filter_string)
        else:
            self.filter = None

ZMIViews = ZMIViewService()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(ZMIViews._clear)
del addCleanUp
