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
from zope.app.location import ILocation, Location

class TrustedAdapterFactory(object):
    """Adapt an adapter factory to to provide trusted adapters

       Trusted adapters always adapt unproxied objects.  If asked to
       adapt any proxied objects, it will unproxy them and then proxy the
       resulting adapter.

       Suppose we have an adapter factory:

         >>> class A(object):
         ...     def __init__(self, context):
         ...         self.context = context

       Now, suppose have an object and proxy it:

         >>> o = []
         >>> p = ProxyFactory(o)

       If we adapt it:

         >>> a = A(p)

       the result is not a proxy:

         >>> type(a).__name__
         'A'

       But the object it adapts still is:

         >>> type(a.context).__name__
         '_Proxy'

       Now, will we'll adapt our adapter factory to a trusted adapter factory:

         >>> TA = TrustedAdapterFactory(A)

       and if we use it:

         >>> a = TA(p)

       then the adapter is proxied:

         >>> type(a).__name__
         '_Proxy'

       And the object proxied is not.  (We actually have to remove the
       adapter to get to the adapted object in this case.)

         >>> a = removeSecurityProxy(a)
         >>> type(a.context).__name__
         'list'

       This works with multiple objects too:

         >>> class M(object):
         ...     def __init__(self, *context):
         ...         self.context = context

         >>> TM = TrustedAdapterFactory(M)

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

       The __parent__ will be set to the first object if the adapter
       is a location. M isn't a location, so the adapter has no
       __parent__:

         >>> a.__parent__
         Traceback (most recent call last):
         ...
         AttributeError: 'M' object has no attribute '__parent__'

       But if we create an adapter that is a Location:

         >>> class L(A, Location):
         ...     pass
         >>> TL = TrustedAdapterFactory(L)

       Then __parent__ will be set:

         >>> TL(o).__parent__ is o
         True
         >>> removeSecurityProxy(TL(p)).__parent__ is o
         True

       The factory adapter has the __name__ and __module__ of the
       factory it adapts:

         >>> (TA.__module__, TA.__name__) == (A.__module__, A.__name__)
         True

       """

    def __init__(self, factory):
        self.factory = factory
        self.__name__ = factory.__name__
        self.__module__ = factory.__module__

    def __call__(self, *args):
        for arg in args:
            if removeSecurityProxy(arg) is not arg:
                args = map(removeSecurityProxy, args)
                adapter = self.factory(*args)
                if (ILocation.providedBy(adapter)
                    and adapter.__parent__ is None):
                    adapter.__parent__ = args[0]
                return ProxyFactory(adapter)

        adapter = self.factory(*args)
        if (ILocation.providedBy(adapter)
            and adapter.__parent__ is None):
            adapter.__parent__ = args[0]
        return adapter
