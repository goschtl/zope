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
$Id: __init__.py,v 1.12 2003/05/27 13:12:10 jim Exp $
"""
__metaclass__ = type

from zope.interface import moduleProvides
from zope.security.proxy import Proxy, getChecker, getObject
from zope.proxy.context.wrapper import getobject, getdict, getdictcreate
from zope.proxy.context.wrapper import getcontext, getinnercontext
from zope.proxy.context.wrapper import getinnerwrapper, getbaseobject
from zope.proxy.context.wrapper import ContextDescriptor, ContextAware
from zope.proxy.context.wrapper import ContextMethod, ContextProperty
from zope.proxy.context.wrapper import Wrapper
from zope.proxy.context.decorator import Decorator
from zope.security.checker import defineChecker, selectChecker, BasicTypes
from zope.proxy.interfaces.context import IContextDecorator
from zope.hookable import hookable

moduleProvides(IContextDecorator)
__all__ = tuple(IContextDecorator)

def ContextWrapper(_ob, _parent, **kw):
    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob

    if type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getObject(_ob)
        _ob = Proxy(makeWrapper(_ob, _parent, kw, checker), checker)
    else:
        _ob = makeWrapper(_ob, _parent, kw)

    if type(_ob) in wrapperTypes:
        #print 'wrapped', _ob
        if getcontext(_ob) == _parent:
            dict = getdictcreate(_ob)
            #print 'avoided rewrapping', dict, kw
            dict.update(kw)
            return _ob




    return _ob

ContextWrapper = hookable(ContextWrapper)

def makeWrapper(ob, parent, kw, checker=None):
    return Wrapper(ob, parent, **kw)
makeWrapper = hookable(makeWrapper)

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
        _ob = Proxy(getobject(_ob), checker)
    else:
        _ob = getobject(_ob)

    return _ob

def _contextWrapperChecker(ob):
    return selectChecker(getobject(ob))

def getWrapperData(_ob, create=False):
    if type(_ob) is Proxy:
        _orig = _ob
        _ob = getObject(_ob)
    if create:
        return getdictcreate(_ob)
    else:
        return getdict(_ob)

def getInnerWrapperData(_ob):
    if type(_ob) is Proxy:
        _ob = getObject(_ob)
    return getdict(getinnerwrapper(_ob))

def getWrapperContainer(_ob):
    if type(_ob) is Proxy:
        _ob = getObject(_ob)
    return getinnercontext(_ob)

def getWrapperContext(_ob):
    if type(_ob) is Proxy:
        _ob = getObject(_ob)
    return getcontext(_ob)

def isWrapper(_ob):
    if type(_ob) is Proxy:
        _ob = getObject(_ob)
    return type(_ob) in wrapperTypes

class ContainmentIterator:

    def __init__(self, obj):
        self._ob = Wrapper(None, obj)

    def __iter__(self):
        return self

    def next(self):
        _ob = self._ob

        if type(_ob) is Proxy:
            _ob = getObject(_ob)

        if type(_ob) not in wrapperTypes:
            raise StopIteration

        _ob = getinnercontext(_ob)
        self._ob = _ob
        return _ob

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

wrapperTypes = (Wrapper, Decorator)

#defineChecker(Wrapper, _contextWrapperChecker)
#defineChecker(Decorator, _contextWrapperChecker)

class ContextSuper:

    def __init__(self, class_, inst):
        self.__inst = inst
        self.__class = class_

    def __getattr__(self, name):
        inst = self.__inst
        return getattr(super(self.__class, getbaseobject(inst)), name
                       ).__get__(inst)
