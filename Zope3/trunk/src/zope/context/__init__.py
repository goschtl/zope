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
$Id: __init__.py,v 1.16 2003/05/28 15:46:51 jim Exp $
"""
from __future__ import generators

__metaclass__ = type


from zope.interface import moduleProvides
from zope.security.proxy import Proxy, getChecker
from zope.context.wrapper import getdict, getdictcreate
from zope.context.wrapper import getcontext, getinnercontext
from zope.context.wrapper import getinnerwrapper, getbaseobject
from zope.context.wrapper import ContextDescriptor, ContextAware
from zope.context.wrapper import ContextMethod, ContextProperty
from zope.context.wrapper import Wrapper
from zope.security.checker import defineChecker, selectChecker, BasicTypes
from zope.proxy import queryProxy, queryInnerProxy, isProxy, getObject
from zope.context.interfaces import IContextWrapper
from zope.hookable import hookable

moduleProvides(IContextWrapper)
__all__ = tuple(IContextWrapper)

def ContextWrapper(_ob, _parent, **kw):
    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob

    if type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getObject(_ob)
        _ob = Proxy(Wrapper(_ob, _parent, **kw), checker)
    else:
        _ob = Wrapper(_ob, _parent, **kw)

    return _ob
ContextWrapper = hookable(ContextWrapper)


def getWrapperObject(_ob):
    """Remove a context wrapper around an object with data

    If the object is wrapped in a security proxy, then the object
    is inserted inside an equivalent security proxy.
    """

    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob
    elif type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getObject(_ob)
        _ob = Proxy(getObject(_ob), checker)
    else:
        _ob = getObject(_ob)

    return _ob

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

def getItem(collection, name):
    return ContextWrapper(collection[name], collection, name=name)

def getAttr(collection, name):
    return ContextWrapper(getattr(collection, name), collection, name=name)

def queryItem(collection, name, default=None):
    return ContextWrapper(collection.get(name, default),
                          collection, name=name)

def queryAttr(collection, name, default=None):
    return ContextWrapper(getattr(collection, name, default),
                          collection, name=name)


# XXX Do I actually need these?
def _contextWrapperChecker(ob):
    return selectChecker(getObject(ob))
defineChecker(Wrapper, _contextWrapperChecker)

class ContextSuper:

    def __init__(self, class_, inst):
        self.__inst = inst
        self.__class = class_

    def __getattr__(self, name):
        inst = self.__inst
        return getattr(super(self.__class, getbaseobject(inst)), name
                       ).__get__(inst)
