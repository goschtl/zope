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
# FOR A PARTICULAR PURPOSE
# 
##############################################################################
"""Wrapping/proxy coordination

Specifically, coordinate use of context wrappers and security proxies.

Revision information:
$Id: ContextWrapper.py,v 1.6 2002/11/30 18:41:33 jim Exp $
"""

from Zope.Security.Proxy import Proxy, getChecker, getObject
from Zope.ContextWrapper import Wrapper as _Wrapper
from Zope.ContextWrapper import wrapperTypes, getobject, getdict
from Zope.ContextWrapper import getcontext, getinnercontext, getinnerwrapper
from Zope.Security.Checker import defineChecker, selectChecker, BasicTypes

from IContextWrapper import IContextWrapper

__implements__ = IContextWrapper

def ContextWrapper(_ob, _parent, **kw):
    """Create a context wrapper around an object with data

    If the object is wrapped in a security proxy, then the context
    wrapper is inserted inside an equivalent security proxy.
    """
    
    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob
    elif type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getObject(_ob)
        _ob = Proxy(_Wrapper(_ob, _parent, **kw), checker)
    else:
        _ob = _Wrapper(_ob, _parent, **kw)
        
    return _ob

def getWrapperObject(_ob):
    """Remove a context wrapper around an object with data

    If the object is wrapped in a security proxy, then the object
    is inserted inside an equivalent  security proxy.
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
    checker = selectChecker(getobject(ob))

defineChecker(_Wrapper, _contextWrapperChecker)

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
        self._ob = _Wrapper(None, obj)

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
