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
$Id: __init__.py,v 1.20 2003/06/07 13:00:01 stevea Exp $
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
