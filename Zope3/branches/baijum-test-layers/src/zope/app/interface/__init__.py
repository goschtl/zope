##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Code about interfaces.

This module contains code for interfaces in persistent modules.

$Id$
"""
__docformat__ = 'restructuredtext'


from persistent import Persistent
from persistent.wref import PersistentWeakKeyDictionary
from zodbcode.patch import registerWrapper, Wrapper

from zope.interface.interface import InterfaceClass
from zope.interface import Interface
from zope.security.proxy import removeSecurityProxy

persistentFactories = {}
def getPersistentKey(v_key):
    if not hasattr(v_key, '__reduce__'):
        return
    reduce = v_key.__reduce__()
    lookups = reduce[0], type(v_key), getattr(v_key, '__class__')
    for lookup in lookups:
        p_factory = persistentFactories.get(lookup, None)
        if p_factory is not None:
            return p_factory(v_key)

class DependentsDict(PersistentWeakKeyDictionary):
    """Intercept non-persistent keys and swap in persistent
    equivalents."""

    def __setstate__(self, state):
        data = state['data']
        for v_key, value in data:
            p_key = getPersistentKey(v_key)
            if p_key is not None:
                data[p_key] = data[v_key]
        state['data'] = data
        return super(DependentsDict, self).__setstate__(state)
                
    def __setitem__(self, key, value):
        p_key = getPersistentKey(key)
        if p_key is not None: key = p_key
        return super(DependentsDict, self).__setitem__(key, value)

    def __len__(self): return len(self.data)

    def get(self, key, default=None):
        if not hasattr(key, '_p_oid') or not hasattr(key, '_p_jar'):
            return default
        return super(DependentsDict, self).get(key, default)

    def update(self, adict):
        for v_key in adict.keys():
            p_key = getPersistentKey(v_key)
            if p_key is not None:
                adict[p_key] = adict[v_key]
        return super(DependentsDict, self).update(adict)

    def keys(self): return [k() for k in self.data.keys()]

from zope.interface.declarations import ProvidesClass, Provides
class PersistentProvidesClass(Persistent, ProvidesClass):
    """A persistent Provides class."""
    def __init__(self, *args, **kw):
        Persistent.__init__(self)
        ProvidesClass.__init__(self, *args, **kw)
        self.dependents = DependentsDict()
def persistentProvides(obj):
    return PersistentProvidesClass(*obj.__reduce__()[1:])
persistentFactories[Provides] = persistentProvides

from zope.interface.declarations import Implements
class PersistentImplements(Persistent, Implements):
    """A persistent Implements class."""
    def __init__(self, *args, **kw):
        Persistent.__init__(self)
        Implements.__init__(self, *args, **kw)
        self.dependents = DependentsDict()
def persistentImplements(obj):
    return PersistentImplements(*obj.__bases__)
persistentFactories[Implements] = persistentImplements

class PersistentInterfaceClass(Persistent, InterfaceClass):

    def __init__(self, *args, **kw):
        Persistent.__init__(self)
        InterfaceClass.__init__(self, *args, **kw)
        
        self.dependents = DependentsDict()

# PersistentInterface is equivalent to the zope.interface.Interface object
# except that it is also persistent.  It is used in conjunction with
# zodb.code to support interfaces in persistent modules.
PersistentInterface = PersistentInterfaceClass("PersistentInterface",
                                               (Interface, ))

class PersistentInterfaceWrapper(Wrapper):

    def unwrap(self):
        return PersistentInterfaceClass(self._obj.__name__)


def getInterfaceStateForPersistentInterfaceCreation(iface):
    # Need to convert the dependents weakref dict to a persistent dict
    dict = iface.__dict__.copy()
    dependents = DependentsDict()
    for k, v in dict['dependents'].iteritems():
        dependents[k] = v
    dict['dependents'] = dependents
    return dict

registerWrapper(InterfaceClass, PersistentInterfaceWrapper,
                lambda iface: (),
                getInterfaceStateForPersistentInterfaceCreation,
                )

from zope.interface.declarations import providedBy

def queryType(object, interface):
    """Returns the object's interface which implements interface.

    >>> from zope.app.content.interfaces import IContentType
    >>> from zope.interface import Interface, implements, directlyProvides
    >>> class I(Interface):
    ...     pass
    >>> class J(Interface):
    ...     pass
    >>> directlyProvides(I, IContentType)
    >>> class C(object):
    ...     implements(I)
    >>> class D(object):
    ...     implements(J,I)
    >>> obj = C()
    >>> c1_ctype = queryType(obj, IContentType)
    >>> c1_ctype.__name__
    'I'
    >>> class I1(I):
    ...     pass
    >>> class I2(I1):
    ...     pass
    >>> class I3(Interface):
    ...     pass
    >>> class C1(object):
    ...     implements(I1)
    >>> obj1 = C1()
    >>> c1_ctype = queryType(obj1, IContentType)
    >>> c1_ctype.__name__
    'I'
    >>> class C2(object):
    ...     implements(I2)
    >>> obj2 = C2()
    >>> c2_ctype = queryType(obj2, IContentType)
    >>> c2_ctype.__name__
    'I'

    >>> class C3(object):
    ...     implements(I3)
    >>> obj3 = C3()

    If Interface doesn't provide `IContentType`, `queryType` returns ``None``.

    >>> c3_ctype = queryType(obj3, IContentType)
    >>> c3_ctype
    >>> c3_ctype is None
    True
    >>> class I4(I):
    ...     pass
    >>> directlyProvides(I4, IContentType)
    >>> class C4(object):
    ...     implements(I4)
    >>> obj4 = C4()
    >>> c4_ctype = queryType(obj4, IContentType)
    >>> c4_ctype.__name__
    'I4'

    """
    # Remove the security proxy, so that we can introspect the type of the
    # object's interfaces.
    naked = removeSecurityProxy(object)
    object_iro = providedBy(naked).__iro__
    for iface in object_iro:
        if interface.providedBy(iface):
            return iface

    return None
