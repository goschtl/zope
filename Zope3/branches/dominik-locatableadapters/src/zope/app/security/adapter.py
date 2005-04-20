##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Support for taking security into account in adaptation

$Id$
"""

from zope.security.checker import ProxyFactory
from zope.security.proxy import removeSecurityProxy
from zope.app.location import ILocation, Location, LocationProxy


class TrustedAdapterFactoryMixin(object):
    """Adapt an adapter factory to to provide trusted adapters

    Trusted adapters always adapt unproxied objects. If asked to
    adapt any proxied objects, it will unproxy them and then security-proxy
    the resulting adapter (S) unless the adapted object were unproxied
    before (N).

    We account two different base use cases S (security-proxied) and N
    (not security-proxied).

        S.  security proxy > adapter > object(s)
        N.  adapter > object(s)
        R.  adapter > security proxy(s) > object(s) (Untrusted adapters)

    Suppose we have an adapter factory:

        >>> class A(object):
        ...     def __init__(self, context):
        ...         self.context = context

    Now, suppose have an object and proxy it:

        >>> o = []
        >>> p = ProxyFactory(o)

    If we adapt it the result is regularly (R) not security-proxied
    but the object it adapts still is:

        >>> a = A(p)
        >>> type(a).__name__
        'A'
        >>> type(a.context).__name__
        '_Proxy'

    Now, will we will adapt our adapter factory to a trusted adapter factory
    mixin:

        >>> TA = TrustedAdapterFactoryMixin(A)

    S. Adaption of security-proxied objects
    If we use it the adapter is security-proxied, but it adapts anymore.
    (We actually have to remove the adapter to get to the adapted object
    in this case.):

        >>> a = TA(p)
        >>> type(a).__name__
        '_Proxy'
        >>> a = removeSecurityProxy(a)
        >>> type(a).__name__
        'A'
        >>> type(a.context).__name__
        'list'

    This works with multiple objects too:

        >>> class M(object):
        ...     def __init__(self, *context):
        ...         self.context = context

        >>> TM = TrustedAdapterFactoryMixin(M)

        >>> o2 = []
        >>> o3 = []

        >>> a = TM(p, o2, o3)
        >>> type(a).__name__
        '_Proxy'
        >>> a = removeSecurityProxy(a)
        >>> a.context[0] is o, a.context[1] is o2, a.context[2] is o3
        (True, True, True)

        >>> a = TM(p, ProxyFactory(o2), ProxyFactory(o3))
        >>> type(a).__name__
        '_Proxy'
        >>> a = removeSecurityProxy(a)
        >>> a.context[0] is o, a.context[1] is o2, a.context[2] is o3
        (True, True, True)

    N. Adaption of none-security-proxied objects
    In cases where the first object that should be adapted is not
    security-proxied the resulting adapter is not security-proxied too:

        >>> a = TA(o)
        >>> type(a).__name__
        'A'
        >>> type(a.context).__name__
        'list'

        >>> a = TM(o, o2, o3)
        >>> type(a).__name__
        'M'
        >>> a.context[0] is o, a.context[1] is o2, a.context[2] is o3
        (True, True, True)

    The factory adapter has the __name__ and __module__ of the
    factory it adapts:

        >>> (TA.__module__, TA.__name__) == (A.__module__, A.__name__)
        True

    """
    def __init__(self, factory):
        self.factory = factory
        self.__name__ = factory.__name__
        self.__module__ = factory.__module__

    # protected methods
    def _customize(self, adapter, context):
        """Subclasses might overwrite this method."""
        return adapter

    def __call__(self, *args):
        for arg in args:
            if removeSecurityProxy(arg) is not arg:
                args = map(removeSecurityProxy, args)
                adapter = self.factory(*args)
                adapter = self._customize(adapter, args[0])
                return ProxyFactory(adapter)

        adapter = self.factory(*args)
        adapter = self._customize(adapter, args[0])
        return adapter


def assertLocation(adapter, parent):
    """Assert locatable adapters.

    This function asserts that the adapter get location-proxied unless it does
    not provide ILocation itself. Further more the returned locatable adapter
    get its parent set unless its __parent__ attribute is not None.
    
    Arguments
    ---------
    adapter - unproxied adapter
    parent - unproxied locatable object

    Usage
    -----
    Suppose we have a location that plays the duty-parent in cases
    where no regular-parent is provided by the adapter itself:

        >>> dutyparent = Location()

    We account three different base use cases A, B and C.
    
    A. Adapters which do not provide ILocation get location-proxied
    and theirs parent is set to the duty-parent:

        >>> class A(object):
        ...     def __init__(self, context):
        ...         self.context = context

        >>> a = A(dutyparent)
        >>> a1 = assertLocation(a, dutyparent)

        >>> ILocation.providedBy(a1)
        True
        >>> a1.__parent__ is dutyparent
        True
        >>> type(a1).__name__
        'LocationProxy'

    B. Adapters which do provide ILocation get never location-proxied,
    but theirs parent is also set to the duty-parent unless their parent is
    not None:

        >>> class B(Location):
        ...     def __init__(self, context):
        ...         self.context = context

        >>> b = B(dutyparent)
        >>> b1 = assertLocation(b, dutyparent)

        >>> ILocation.providedBy(b1)
        True
        >>> b1.__parent__ is dutyparent
        True
        >>> type(b1).__name__
        'B'

    C. In those cases where the parent is provided by the adapter itself, the
    adapter keeps its regular-parent:

        >>> regularparent = Location()

        >>> class C(Location):
        ...     def __init__(self, context):
        ...         self.context = context
        ...         self.__parent__ = context

        >>> c = C(regularparent)
        >>> c1 = assertLocation(c, dutyparent)

        >>> ILocation.providedBy(c1)
        True
        >>> c1.__parent__ is regularparent
        True
        >>> type(c1).__name__
        'C'
    """
    # handle none-locatable adapters (A)
    if not ILocation.providedBy(adapter):
        locatable = LocationProxy(adapter)
        locatable.__parent__ = parent
        return locatable

    # handle locatable, parentless adapters (B)
    if adapter.__parent__ is None:
        adapter.__parent__ = parent
        return adapter

    # handle locatable, parentful adapters (C)
    else:
        return adapter


# BBB: The trusted adapter factory is replaced by the locating trusted adapter
# factory
class TrustedAdapterFactory(TrustedAdapterFactoryMixin):
    """Adapt an adapter factory to to provide trusted adapters

    Trusted adapters always adapt unproxied objects.  If asked to
    adapt any proxied objects, it will unproxy them and then 
    security-proxy the resulting adapter unless the objects where not
    security-proxied before.

    Further this adapter factory sets the __parent__ attribute of locatable
    object (ILocation) unless those objects do not provide their parent
    itself.

    We account three different base use cases A, B and C (corresponding 
    to def assertLocation()) each of them provided two variantions S and
    N corresponding to class TrustedAdapterFactoryMixin).

    Now, suppose have an object and proxy it:

        >>> o = []
        >>> p = ProxyFactory(o)

    A. Unlocatable adatpers

        >>> class A(object):
        ...     def __init__(self, context):
        ...         self.context = context

        >>> TA = TrustedAdapterFactory(A)

    AS. Security-proxied:

        >>> a = TA(p)
        >>> a.__parent__
        Traceback (most recent call last):
        ...
        AttributeError: 'A' object has no attribute '__parent__'
        >>> type(a).__name__
        '_Proxy'

    AN. None-security-proxied:

        >>> a = TA(o)
        >>> a.__parent__
        Traceback (most recent call last):
        ...
        AttributeError: 'A' object has no attribute '__parent__'
        >>> type(a).__name__
        'A'

    B. Locatable, but parentless adapters

        >>> class B(Location):
        ...     def __init__(self, context):
        ...         self.context = context


        >>> TB = TrustedAdapterFactory(B)

    BS. Security-proxied:

        >>> a = TB(p)
        >>> removeSecurityProxy(a.__parent__) is o
        True
        >>> type(a).__name__
        '_Proxy'

    BS. None-security-proxied:

        >>> a = TB(o)
        >>> a.__parent__ is o
        True
        >>> type(a).__name__
        'B'

    C. Locatable and parentful adapter

        >>> marker = Location()

        >>> class C(Location):
        ...     def __init__(self, context):
        ...         self.context = context
        ...         self.__parent__ = marker


        >>> TC = TrustedAdapterFactory(C)

    CS. Security-proxied:

        >>> a = TC(p)
        >>> removeSecurityProxy(a.__parent__) is marker
        True
        >>> type(a).__name__
        '_Proxy'

    CS. None-security-proxied:

        >>> a = TC(o)
        >>> a.__parent__ is marker
        True
        >>> type(a).__name__
        'C'
    """

    def _customize(self, adapter, context):
        if (ILocation.providedBy(adapter)
            and adapter.__parent__ is None):
                    adapter.__parent__ = context
        return adapter



class LocatingTrustedAdapterFactory(TrustedAdapterFactoryMixin):
    """Adapt an adapter factory to to provide trusted locatable adapters

    Trusted adapters always adapt unproxied objects.  If asked to
    adapt any proxied objects, it will unproxy them and then 
    security-proxy the resulting adapter unless the objects where not
    security-proxied before.

    Further locating trusted adapters always provide a location.
    If an adapter itself does not provide ILocation it is wrapped 
    within a location proxy and it parent will be set:

        security proxy > location proxy > adapter > object(s)

    If the adapter does provide ILocation and it's __parent__ is None,
    we set the __parent__ only: 
    
        security proxy > adapter > object(s) 

    Now, suppose have an object and proxy it:

        >>> o = []
        >>> p = ProxyFactory(o)

    A. Unlocatable adatpers

        >>> class A(object):
        ...     def __init__(self, context):
        ...         self.context = context

        >>> TA = LocatingTrustedAdapterFactory(A)

    AS. Security-proxied:

        >>> a = TA(p)
        >>> removeSecurityProxy(a.__parent__) is o
        True
        >>> type(a).__name__
        '_Proxy'
        >>> type(removeSecurityProxy(a)).__name__
        'LocationProxy'
        >>> from zope.proxy import removeAllProxies
        >>> type(removeAllProxies(a)).__name__
        'A'

    AN. None-security-proxied:

        >>> a = TA(o)
        >>> a.__parent__ is o
        True
        >>> type(a).__name__
        'LocationProxy'
        >>> type(removeAllProxies(a)).__name__
        'A'

    B. Locatable, but parentless adapters

        >>> class B(Location):
        ...     def __init__(self, context):
        ...         self.context = context


        >>> TB = LocatingTrustedAdapterFactory(B)

    BS. Security-proxied:

        >>> a = TB(p)
        >>> removeSecurityProxy(a.__parent__) is o
        True
        >>> type(a).__name__
        '_Proxy'

    BS. None-security-proxied:

        >>> a = TB(o)
        >>> a.__parent__ is o
        True
        >>> type(a).__name__
        'B'

    C. Locatable and parentful adapter

        >>> marker = Location()

        >>> class C(Location):
        ...     def __init__(self, context):
        ...         self.context = context
        ...         self.__parent__ = marker


        >>> TC = LocatingTrustedAdapterFactory(C)

    CS. Security-proxied:

        >>> a = TC(p)
        >>> removeSecurityProxy(a.__parent__) is marker
        True
        >>> type(a).__name__
        '_Proxy'

    CS. None-security-proxied:

        >>> a = TC(o)
        >>> a.__parent__ is marker
        True
        >>> type(a).__name__
        'C'
    """

    def _customize(self, adapter, context):
        return assertLocation(adapter, context)


class LocatingUntrustedAdapterFactory(object):
    """Adapt an adapter factory to provide locatable untrusted adapters

    Untrusted adapters always adapt proxied objects. If any permission
    other than zope.Public is required, untrusted adapters need a location
    in order that the local authentication mechanism can be inovked
    correctly.

    If the adapter does not provide ILocation, we location proxy it and
    set the parent:
    
        location proxy > adapter > security proxy > object(s) 
    
    If the adapter does provide ILocation and it's __parent__ is None,
    we set the __parent__ only:

        adapter > security proxy > object(s)

    Now, suppose have an object and proxy it:

      o = []
      >>> o = []
      >>> p = ProxyFactory(o)

    A. Adapters which do not provide ILocation get location-proxied
    and theirs parent is set:

        >>> class A(object):
        ...     def __init__(self, context):
        ...         self.context = context

        >>> UA = LocatingUntrustedAdapterFactory(A)
        >>> a = UA(o)

        >>> ILocation.providedBy(a)
        True
        >>> a.__parent__ is o
        True
        >>> type(a).__name__
        'LocationProxy'
        >>> from zope.proxy import removeAllProxies
        >>> type(removeAllProxies(a)).__name__
        'A'

    B. Adapters which do provide ILocation get never location-proxied,
    but theirs parent is also set unless their parent is
    not None:

        >>> class B(Location):
        ...     def __init__(self, context):
        ...         self.context = context

        >>> UB = LocatingUntrustedAdapterFactory(B)
        >>> b = UB(o)

        >>> ILocation.providedBy(b)
        True
        >>> b.__parent__ is o
        True
        >>> type(b).__name__
        'B'

    C. In those cases where the parent is provided by the adapter itself,
    nothing happens:

        >>> class C(Location):
        ...     def __init__(self, context):
        ...         self.context = context
        ...         self.__parent__ = context

        >>> UC = LocatingUntrustedAdapterFactory(C)
        >>> c = UC(o)

        >>> ILocation.providedBy(c)
        True
        >>> c.__parent__ is o
        True
        >>> type(c).__name__
        'C'

     The factory adapter has the __name__ and __module__ of the
     factory it adapts:

         >>> (UB.__module__, UB.__name__) == (B.__module__, B.__name__)
         True
    """

    def __init__(self, factory):
        self.factory = factory
        self.__name__ = factory.__name__
        self.__module__ = factory.__module__

    def __call__(self, *args):
        adapter = self.factory(*args)
        return assertLocation(adapter, args[0])
