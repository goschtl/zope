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
"""Wrapping/proxy coordination

Specifically, coordinate use of context wrappers and security proxies.

Revision information:
$Id: __init__.py,v 1.21 2003/06/07 19:05:20 stevea Exp $
"""
from __future__ import generators

__metaclass__ = type

from zope.interface import moduleProvides
from zope.context.wrapper import getdict, getdictcreate
from zope.context.wrapper import getcontext, getinnercontext
from zope.context.wrapper import getinnerwrapper, getbaseobject
from zope.context.wrapper import ContextDescriptor, ContextMethod
from zope.context.wrapper import ContextProperty, Wrapper
from zope.proxy import queryProxy, queryInnerProxy, isProxy, getProxiedObject
from zope.context.interfaces import IWrapperIntrospection

moduleProvides(IWrapperIntrospection)
__all__ = tuple(IWrapperIntrospection)

def getWrapperData(_ob, create=False):
    wrapper = queryProxy(_ob, Wrapper)
    if wrapper is not None:
        if create:
            return getdictcreate(wrapper)
        else:
            return getdict(wrapper)
    else:
        if create:
            raise TypeError("Not a context wrapper")
        return None

def getInnerWrapperData(_ob):
    wrapper = queryInnerProxy(_ob, Wrapper)
    if wrapper is not None:
        return getdict(wrapper)
    else:
        return None

def getWrapperContainer(_ob):
    wrapper = queryInnerProxy(_ob, Wrapper)
    if wrapper is not None:
        return getcontext(wrapper)
    else:
        return None

def getWrapperContext(_ob):
    wrapper = queryProxy(_ob, Wrapper)
    if wrapper is not None:
        return getcontext(wrapper)
    else:
        return None

def isWrapper(_ob):
    return isProxy(_ob, Wrapper)

def ContainmentIterator(obj):
    wrapper = queryInnerProxy(obj, Wrapper)
    while wrapper is not None:
        yield obj
        obj = getcontext(wrapper)
        wrapper = queryInnerProxy(obj, Wrapper)

    yield obj

def ContextIterator(obj):
    wrapper = queryProxy(obj, Wrapper)
    while wrapper is not None:
        yield obj
        obj = getcontext(wrapper)
        wrapper = queryProxy(obj, Wrapper)

    yield obj

class ContextSuper:

    def __init__(self, class_, inst):
        self.__inst = inst
        self.__class = class_

    def __getattr__(self, name):
        inst = self.__inst
        return getattr(super(self.__class, getbaseobject(inst)), name
                       ).__get__(inst)

class ContextAwareDescriptor(ContextDescriptor):
    # TODO For speed, reimplement this in C

    def __init__(self, descriptor):
        self.descriptor = descriptor

    def __get__(self, inst, cls=None):
        return self.descriptor.__get__(inst, cls)

    def getdoc(self):
        return self.descriptor.__doc__

    __doc__ = property(getdoc)

class ContextAwareDataDescriptor(ContextAwareDescriptor):

    def __set__(self, inst, value):
        self.descriptor.__set__(inst, value)

    def __delete__(self, inst):
        self.descriptor.__delete__(inst)


class ContextAwareMetaClass(type):

    def __init__(self, name, bases, namespace):
        # stub
        super(ContextAwareMetaClass, self).__init__(name, bases, namespace)


class ContextAware:
    __metaclass__ = ContextAwareMetaClass


def init_method(self, name, bases, namespace):
    if ContextAware in bases:
        for name, obj in namespace.items():
            if not isinstance(obj, ContextDescriptor):
                if getattr(obj, '__set__', None) is not None:
                    d = ContextAwareDataDescriptor(obj)
                    setattr(self, name, d)
                    namespace[name] = d
                elif getattr(obj, '__get__', None) is not None:
                    m = ContextAwareDescriptor(obj)
                    setattr(self, name, m)
                    namespace[name] = m
    super(ContextAwareMetaClass, self).__init__(name, bases, namespace)
ContextAwareMetaClass.__init__ = init_method
del init_method
