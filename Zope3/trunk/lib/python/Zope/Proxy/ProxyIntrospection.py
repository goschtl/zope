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

# XXX this module should bnecome unnecessary

"""Temporary hack module until there is a generic way to deal with proxies

This module provides some standard machinery to recognize and remove
proxies. It is hoped that it will be replaced by a cleaner
implementation based on a common proxy base class.

This module requires that proxy implementations register themselvss
with the module, by calling defineProxyType, however, it
short-circuits the definitions for two types, which, hopefully will be
the only two types that need to get registered. ;)

$Id: ProxyIntrospection.py,v 1.4 2002/12/13 23:06:46 jeremy Exp $
"""
from IProxyIntrospection import IProxyIntrospection

__implements__ = IProxyIntrospection


from Zope.Exceptions import DuplicationError

class ProxyRegistry:

    def __init__(self):
        self._proxy_types = {}

        # register security proxy
        from Zope.Security.Proxy import Proxy, getObject
        self._proxy_types[Proxy] = getObject

        # register context wrappers
        from Zope.ContextWrapper import wrapperTypes, getobject
        for wrapper_type in wrapperTypes:
            self._proxy_types[wrapper_type] = getobject
        
    _clear = __init__

    def defineProxyType(self, type_, remover):
        """Register a proxy type
        
        A type and a function are provides. The function should take a
        proxy and return the object proxied.
        """
        if type_ in self._proxy_types:
            raise DuplicationError(type_)

        self._proxy_types[type_] = remover

    def removeProxy(self, obj):
        """Return the immediately proxied object.

        If obj is not a proxied object, return obj.

        Note that the object returned may still be a proxy, if there
        are multiple layers of proxy.
        
        """
        remover = self._proxy_types.get(type(obj))
        if remover is None:
            return obj

        return remover(obj)
        

    def removeAllProxies(self, obj):
        """Get the proxied oject with no proxies

        If obj is not a proxied object, return obj.

        The returned object has no proxies.
        """

        i=0
        get = self._proxy_types.get
        while i < 100:
            remover = get(type(obj))
            if remover is None:
                return obj
            
            obj = remover(obj)
            i=i+1

        raise TypeError('excessive proxy nesting')

    def isProxy(self, obj):
        """Check whether the given object is a proxy
        """
        return type(obj) in self._proxy_types
    
theProxyRegistry = ProxyRegistry()

isProxy = theProxyRegistry.isProxy
removeProxy = theProxyRegistry.removeProxy
removeAllProxies = theProxyRegistry.removeAllProxies
_clear = theProxyRegistry._clear
