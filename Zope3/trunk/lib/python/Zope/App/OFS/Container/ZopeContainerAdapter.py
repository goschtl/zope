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

Revision information:
$Id: ZopeContainerAdapter.py,v 1.2 2002/11/18 23:52:58 jim Exp $
"""

from Zope.App.OFS.Container.IZopeContainer import IZopeContainer
from Zope.ComponentArchitecture import queryAdapter
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Event import publishEvent
from Zope.Event.ObjectEvent \
     import ObjectRemovedEvent, ObjectModifiedEvent, ObjectAddedEvent
from Zope.App.OFS.Container.IAddNotifiable import IAddNotifiable
from Zope.App.OFS.Container.IDeleteNotifiable import IDeleteNotifiable
from types import StringTypes
from Zope.Proxy.ProxyIntrospection import removeAllProxies

_marker = object()

class ZopeContainerAdapter:
    
    __implements__ =  IZopeContainer

    def __init__(self, container):
        self.context = container
        
    def __getitem__(self, key):
        "See Zope.App.OFS.Container.IZopeContainer.IZopeItemContainer"
        value = self.context[key]
        return ContextWrapper(value, self.context, name=key)

    def get(self, key, default=None):
        "See Zope.App.OFS.Container.IZopeContainer.IZopeSimpleReadContainer"
        value = self.context.get(key, _marker)
        if value is not _marker:
            return ContextWrapper(value, self.context, name=key)
        else:
            return default

    def __contains__(self, key):
        '''See interface IReadContainer'''
        return key in self.context
            

    def values(self):
        "See Zope.App.OFS.Container.IZopeContainer.IZopeReadContainer"
        container = self.context
        result = []
        for key, value in container.items():
            result.append(ContextWrapper(value, container, name=key))             
        return result
    
    def keys(self):
        '''See interface IReadContainer'''
        return self.context.keys()

    def __len__(self):
        '''See interface IReadContainer'''
        return len(self.context)    

    def items(self):
        "See Zope.App.OFS.Container.IZopeContainer.IZopeReadContainer"
        container = self.context
        result = []
        for key, value in container.items():
            result.append((key, ContextWrapper(value, container, name=key)))
        return result
        

    def setObject(self, key, object):
        "See Zope.App.OFS.Container.IZopeContainer.IZopeWriteContainer"
        
        if type(key) in StringTypes and len(key)==0:
            raise ValueError("The id cannot be an empty string")

        # We remove the proxies from the object before adding it to
        # the container, because we can't store proxies.
        object = removeAllProxies(object)

        # Add the object
        container = self.context
        key = container.setObject(key, object)

        # Publish an added event
        object = ContextWrapper(container[key], container, name=key)
        publishEvent(container, ObjectAddedEvent(object))

        # Call the after add hook, if necessary
        adapter = queryAdapter(object, IAddNotifiable)
        if adapter is not None:
            adapter.manage_afterAdd(object, container)

        publishEvent(container, ObjectModifiedEvent(container))
        return key

    def __delitem__(self, key):
        "See Zope.App.OFS.Container.IZopeContainer.IZopeWriteContainer"
        container = self.context
        
        object = container[key]
        object = ContextWrapper(object, container, name=key)
        
        # Call the before delete hook, if necessary
        adapter = queryAdapter(object, IDeleteNotifiable)
        if adapter is not None:
            adapter.manage_beforeDelete(object, container)
            
            
        del container[key]

        publishEvent(container, ObjectRemovedEvent(object))
        publishEvent(container, ObjectModifiedEvent(container))

        return key
