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
$Id: __init__.py,v 1.3 2003/01/25 15:32:50 jim Exp $
"""

from zope.security.proxy import Proxy, getChecker, getObject
from zope.proxy.context.wrapper import getobject, getdict
from zope.proxy.context.wrapper import getcontext, getinnercontext
from zope.proxy.context.wrapper import getinnerwrapper
from zope.proxy.context.wrapper import Wrapper as _Wrapper, getbaseobject
from zope.security.checker import defineChecker, selectChecker, BasicTypes


__metaclass__ = type

from zope.proxy.interfaces.context import IContextWrapper

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
        _ob = Proxy(wrapperCreator(_ob, _parent, **kw), checker)
    else:
        _ob = wrapperCreator(_ob, _parent, **kw)

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
        self._ob = wrapperCreator(None, obj)

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



##############################################################################
#
# Approach
#
# The facilities here work by adding markers on methods or properties
# that a custom wrapper class looks for.  We rely on the custom
# wrapper class's __getattribute__ to rebind things on the way out.
#
# For further discission, see this wiki page (all on one line):
# http://dev.zope.org/Wikis/DevSite/Projects/ComponentArchitecture/...
# zope.proxy.context.ContextMethod
#
##############################################################################


# This method wrapper does not work for builtin methods.

class ContextMethod:
    def __new__(cls, method):
        try:
            method.__Zope_ContextWrapper_contextful_get__ = True
        except AttributeError:
            raise TypeError(
                "Cannot make %s into a contextmethod" % type(method)
                )
        return method

class ContextAware:
    """Marker class indicating that all descriptors should be bound in context
    """

class ContextProperty(property):
    """A property that provides a context wrapper to its getter and setter
    methods"""
    __Zope_ContextWrapper_contextful_get__ = True
    __Zope_ContextWrapper_contextful_set__ = True

class ContextGetProperty(property):
    """A property that provides a context wrapper to its getter method"""
    __Zope_ContextWrapper_contextful_get__ = True

class ContextSetProperty(property):
    """A property that provides a context wrapper to its setter method"""
    __Zope_ContextWrapper_contextful_set__ = True

def wrapperCreator(object, context=None, **data):
    has_call = (hasattr(object, '__call__') and
                getattr(object.__call__,
                        '__Zope_ContextWrapper_contextful_get__', False))
    has_getitem = (hasattr(object, '__getitem__') and
                   getattr(object.__getitem__,
                           '__Zope_ContextWrapper_contextful_get__', False))
    if has_call and has_getitem:
        factory = SimpleCallableGetitemMethodWrapper
    elif has_call:
        factory = SimpleCallableMethodWrapper
    elif has_getitem:
        factory = SimpleGetitemMethodWrapper
    else:
        factory = SimpleMethodWrapper

    return factory(object, context, **data)

Wrapper = wrapperCreator

class SimpleMethodWrapper(_Wrapper):

    def __getattribute__(self, name):
        """Support for ContextMethod and ContextProperty.__get__"""
        obj = getbaseobject(self)
        class_ = obj.__class__
        class_value = getattr(class_, name, None)
        if hasattr(class_value, '__get__'):
            if (isinstance(obj, ContextAware)
                or
                getattr(class_value,
                       '__Zope_ContextWrapper_contextful_get__', False)
                ):
                return class_value.__get__(self, class_)

        return _Wrapper.__getattribute__(self, name)

    def __setattr__(self, name, value):
        """Support for ContextProperty.__set__"""
        obj = getbaseobject(self)
        class_ = obj.__class__
        class_value = getattr(class_, name, None)
        if hasattr(class_value, '__set__'):
            if (isinstance(obj, ContextAware)
                or
                getattr(class_value,
                       '__Zope_ContextWrapper_contextful_set__', False)
                ):
                class_value.__set__(self, value)
                return
        setattr(obj, name, value)


class SimpleCallableMethodWrapper(SimpleMethodWrapper):

    def __call__(self, *args, **kw):
        attr = _Wrapper.__getattribute__(self, '__call__')
        return attr.__get__(self)(*args, **kw)

class SimpleGetitemMethodWrapper(SimpleMethodWrapper):

    def __getitem__(self, key, *args, **kw):
        attr = _Wrapper.__getattribute__(self, '__getitem__')
        return attr.__get__(self)(key, *args, **kw)

class SimpleCallableGetitemMethodWrapper(SimpleCallableMethodWrapper,
                                         SimpleGetitemMethodWrapper):
    pass

wrapperTypes = (SimpleMethodWrapper, SimpleCallableMethodWrapper,
                SimpleGetitemMethodWrapper,
                SimpleCallableGetitemMethodWrapper)

for wrapper_type in wrapperTypes:
    defineChecker(wrapper_type, _contextWrapperChecker)

class ContextSuper:

    def __init__(self, class_, inst):
        self.__inst = inst
        self.__class = class_

    def __getattr__(self, name):
        inst = self.__inst
        return getattr(super(self.__class, getbaseobject(inst)), name
                       ).__get__(inst)
