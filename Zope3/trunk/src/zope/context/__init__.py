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
$Id: __init__.py,v 1.7 2003/05/01 19:35:45 faassen Exp $
"""
__metaclass__ = type

from zope.interface import moduleProvides
from zope.security.proxy import Proxy, getChecker, getObject
from zope.proxy.context.wrapper import getobject, getdict
from zope.proxy.context.wrapper import getcontext, getinnercontext
from zope.proxy.context.wrapper import getinnerwrapper, getbaseobject
from zope.proxy.context.wrapper import ContextDescriptor, ContextAware
from zope.proxy.context.wrapper import ContextMethod, ContextProperty
from zope.proxy.context.wrapper import Wrapper
from zope.security.checker import defineChecker, selectChecker, BasicTypes

from zope.proxy.interfaces.context import IContextWrapper

moduleProvides(IContextWrapper)

def ContextWrapper(_ob, _parent, **kw):
    """Create a context wrapper around an object with data

    If the object is wrapped in a security proxy, then the context
    wrapper is inserted inside an equivalent security proxy.
    """

    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob

##     if type(_ob.__class__) is ClassType:
##         # We have an instance of a classic class.
##         # This isn't *too* bad in itself, but we're going to make sure that
##         # it doesn't have any ContextDescriptor members.
##         cls = _ob.__class__
                    
##         for name, member in inspect.getmembers(cls):
##             if isinstance(member, ContextDescriptor):
##                 raise TypeError("Class %s is a classic class, but has a"
##                                 " ContextDescriptor member '%s'. This member"
##                                 " will not work properly." %
##                                 (cls, name))

    if type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getObject(_ob)
        _ob = Proxy(Wrapper(_ob, _parent, **kw), checker)
    else:
        _ob = Wrapper(_ob, _parent, **kw)

    return _ob

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

def getWrapperData(_ob):
    if type(_ob) is Proxy:
        _ob = getObject(_ob)
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

wrapperTypes = (Wrapper,)

defineChecker(Wrapper, _contextWrapperChecker)

class ContextSuper:

    def __init__(self, class_, inst):
        self.__inst = inst
        self.__class = class_

    def __getattr__(self, name):
        inst = self.__inst
        return getattr(super(self.__class, getbaseobject(inst)), name
                       ).__get__(inst)
