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
$Id: context.py,v 1.11 2003/07/01 23:28:42 jim Exp $
"""

from pickle import PicklingError
from zope.app.interfaces.context import IContextWrapper, IZopeContextWrapper
from zope.component import queryAdapter
from zope.context.wrapper import getcontext, setcontext, getdictcreate
from zope.context.wrapper import Wrapper as BaseWrapper
from zope.interface.declarations import getObjectSpecification
from zope.interface.declarations import ObjectSpecification
from zope.interface.declarations import ObjectSpecificationDescriptor
from zope.interface import moduleProvides, implements, providedBy
from zope.proxy import queryProxy, getProxiedObject, sameProxiedObjects
from zope.security.checker import defineChecker, BasicTypes
from zope.security.checker import selectChecker, CombinedChecker, NoProxy
from zope.security.proxy import Proxy, getChecker

moduleProvides(IContextWrapper)
__all__ = tuple(IContextWrapper)
__metaclass__ = type

class DecoratorSpecificationDescriptor(ObjectSpecificationDescriptor):
    """Support for interface declarations on decorators

    >>> from zope.interface import *
    >>> class I1(Interface):
    ...     pass
    >>> class I2(Interface):
    ...     pass
    >>> class I3(Interface):
    ...     pass
    >>> class I4(Interface):
    ...     pass

    >>> class D1(Wrapper):
    ...   implements(I1)


    >>> class D2(Wrapper):
    ...   implements(I2)

    >>> class X:
    ...   implements(I3)

    >>> x = X()
    >>> directlyProvides(x, I4)

    Interfaces of X are ordered with the directly-provided interfaces first

    >>> [interface.__name__ for interface in list(providedBy(x))]
    ['I4', 'I3']

    When we decorate objects, what order should the interfaces come
    in?  One could argue that decorators are less specific, so they
    should come last.

    >>> [interface.__name__ for interface in list(providedBy(D1(x)))]
    ['I4', 'I3', 'I1']

    >>> [interface.__name__ for interface in list(providedBy(D2(D1(x))))]
    ['I4', 'I3', 'I1', 'I2']
    """
    def __get__(self, inst, cls=None):
        if inst is None:
            return getObjectSpecification(cls)
        else:
            provided = providedBy(getProxiedObject(inst))

            # Use type rather than __class__ because inst is a proxy and
            # will return the proxied object's class.
            cls = type(inst) 
            return ObjectSpecification(provided, cls)


class DecoratedSecurityCheckerDescriptor:
    """Descriptor for a Wrapper that provides a decorated security checker.
    """
    def __get__(self, inst, cls=None):
        if inst is None:
            return self
        else:
            proxied_object = getProxiedObject(inst)
            checker = getattr(proxied_object, '__Security_checker__', None)
            if checker is None:
                checker = selectChecker(proxied_object)
            wrapper_checker = selectChecker(inst)
            if wrapper_checker is None:
                return checker
            elif checker is None:
                return wrapper_checker
            else:
                return CombinedChecker(wrapper_checker, checker)


class Wrapper(BaseWrapper):
    """Zope-specific context wrapper
    """
    __slots__ = ()

    def __reduce_ex__(self, proto=None):
        raise PicklingError, "Zope context wrappers cannot be pickled"

    __reduce__ = __reduce_ex__

    __providedBy__ = DecoratorSpecificationDescriptor()

    __Security_checker__ = DecoratedSecurityCheckerDescriptor()


def ContextWrapper(_ob, _parent, **kw):
    if type(_ob) in BasicTypes:
        # Don't wrap basic objects
        return _ob

    wrapper = queryProxy(_ob, Wrapper)
    if wrapper is not None: # using kw as marker

        wrappercontext = getcontext(wrapper)


        if (_parent is wrappercontext

            # Check after removing a security proxy
            or
            (sameProxiedObjects(_parent, wrappercontext)
             and 
             issubclass(type(_parent), Proxy)
             and
             getProxiedObject(_parent) is wrappercontext
             )
            ):

            # This would be a redundant wrapper. We'll just use the
            # one we've got.

            if wrappercontext is not _parent:
                setcontext(wrapper, _parent)

            # But we want tp make sure we have the same data
            if kw:
                getdictcreate(wrapper).update(kw)
            return _ob

    if type(_ob) is Proxy:
        # insert into proxies
        checker = getChecker(_ob)
        _ob = getProxiedObject(_ob)
    else:
        checker = None

    if wrapper is not None:
        # we were already wrapped, use the same class
        _ob = type(wrapper)(_ob, _parent, **kw)
    else:
        adapter = queryAdapter(_ob, IZopeContextWrapper)
        if adapter is not None:
            _ob = adapter
            setcontext(_ob, _parent)
            if kw:
                getdictcreate(_ob).update(kw)
        else:
            # No specific adapter, fall back to Wrapper
            _ob = Wrapper(_ob, _parent, **kw)

    if checker is not None:
        # XXX Problem here is if the wrapper requires a different checker
        # Let's make a combined checker using the checker we have.
        # This is similar to what the DecoratedSecurityCheckerDescriptor
        # does. (See above.)
        # This behaviour needs a test.
        wrapper_checker = selectChecker(_ob)
        if wrapper_checker is not None:
            checker = CombinedChecker(wrapper_checker, checker)
        _ob = Proxy(_ob, checker)

    return _ob

defineChecker(Wrapper, NoProxy)

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
