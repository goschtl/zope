##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""proxy code for shortcut package

$Id: proxy.py 1585 2005-05-09 15:06:51Z gary $
"""
from zope import interface, proxy
from zope.interface import declarations
try:
    from zope.security.decorator import DecoratedSecurityCheckerDescriptor
except ImportError:
    # BBB 2006/09/25 -- to be removed when Zope 3.3 is not supported any more.
    from zope.decorator import DecoratedSecurityCheckerDescriptor
from zc.shortcut import interfaces

class DecoratorSpecificationDescriptor(
    declarations.ObjectSpecificationDescriptor):
    """interface declarations on decorators that wish to have their interfaces
    be the most specific, rather than the least (as in 
    DecoratorSpecificationDescriptor)."""
    
    # As of version 3.4, zope.interface has an unbounded cache of Declaration
    # objects.  This resulted in unbound memory growth when doing lots of
    # adaptations of zc.shortcut proxies.  To avoid the problem until
    # zope.interface is changed, we essentially memoize the creation of these
    # objects.
    declaration_cache = {}

    def __get__(self, inst, cls=None):
        if inst is None:
            return declarations.getObjectSpecification(cls)
        else:
            provided = interface.providedBy(proxy.getProxiedObject(inst))
            # Use type rather than __class__ because inst is a proxy and
            # will return the proxied object's class.
            dec_impl = interface.implementedBy(type(inst))
            result = self.declaration_cache.get( (dec_impl, provided) )
            if result is None:
                result = declarations.Declaration(dec_impl, provided)
                self.declaration_cache[dec_impl, provided] = result
            return result

    def __set__(self, inst, v):
        raise TypeError("assignment not allowed")

class Decorator(proxy.ProxyBase):
    "Overriding specification decorator base class"
    __providedBy__ = DecoratorSpecificationDescriptor()
    __Security_checker__ = DecoratedSecurityCheckerDescriptor()

class DecoratorProvidesDescriptor(object):

    def __get__(self, inst, cls):
        if inst is None:
            # We were accessed through a class, so we are the class'
            # provides spec. Just return this object as is:
            return self

        return proxy.getProxiedObject(inst).__provides__

    def __set__(self, inst, value):
        proxy.getProxiedObject(inst).__provides__ = value

    def __delete__(self, inst):
        del proxy.getProxiedObject(inst).__provides__

def proxyImplements(cls, *interfaces):
    interface.classImplements(cls, *interfaces)
    if type(cls.__provides__) is not DecoratorProvidesDescriptor:
        cls.__provides__ = DecoratorProvidesDescriptor()

def implements(*interfaces):
    declarations._implements("implements", interfaces, proxyImplements)

class ClassAndInstanceDescr(object):
    def __init__(self, *args):
        self.funcs = args

    def __get__(self, inst, cls):
        if inst is None:
            return self.funcs[1](cls)
        return self.funcs[0](inst)

    def __set__(self, inst, v):
        raise TypeError("assignment not allowed")

class ProxyBase(proxy.ProxyBase):

    __slots__ = '__traversed_parent__', '__traversed_name__'

    def __new__(self, ob, parent, name):
        return proxy.ProxyBase.__new__(self, ob)

    def __init__(self, ob, parent, name):
        proxy.ProxyBase.__init__(self, ob)
        self.__traversed_parent__ = parent
        self.__traversed_name__ = name

    __doc__ = ClassAndInstanceDescr(
        lambda inst: proxy.getProxiedObject(inst).__doc__,
        lambda cls, __doc__ = __doc__: __doc__,
        )

    __providedBy__ = DecoratorSpecificationDescriptor()

    __Security_checker__ = DecoratedSecurityCheckerDescriptor()

class Proxy(ProxyBase):
    implements(interfaces.ITraversalProxy)

class TargetProxy(ProxyBase):
    implements(interfaces.ITargetProxy)
    __slots__ = '__shortcut__',

    def __new__(self, ob, parent, name, shortcut):
        return ProxyBase.__new__(self, ob, parent, name)

    def __init__(self, ob, parent, name, shortcut):
        ProxyBase.__init__(self, ob, parent, name)
        self.__shortcut__ = shortcut

class ShortcutProxy(Proxy):

    @property
    def target(self):
        shortcut = proxy.getProxiedObject(self)
        return TargetProxy(
            shortcut.raw_target, self.__traversed_parent__, 
            self.__traversed_name__, shortcut)

def removeProxy(obj):
    p = proxy.queryInnerProxy(obj, ProxyBase)
    if p is None:
        return obj
    else:
        return proxy.getProxiedObject(p)
