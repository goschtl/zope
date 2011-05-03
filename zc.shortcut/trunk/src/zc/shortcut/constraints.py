##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Container constraints for shortcuts

$Id: constraints.py 1832 2005-05-26 16:14:15Z gary $
"""
import sys

from zope import interface
from zope.app.container.interfaces import InvalidItemType, IContainer

from zc.shortcut import interfaces, Shortcut

class ShortcutTypePrecondition(object):
    """a `__setitem__` precondition that restricts shortcut target types

    Items must be one of the given types.  

    >>> class I1(interface.Interface):
    ...     pass
    >>> class I2(interface.Interface):
    ...     pass


    >>> precondition = ShortcutTypePrecondition(I1, I2)
    >>> types_precondition = ShortcutTypePrecondition(types=(I1, I2))
    >>> mixed_precondition = ShortcutTypePrecondition(I2, types=(I2,))

    >>> class Ob(object):
    ...     pass
    >>> ob = Ob()
    >>> shortcut = Shortcut(ob)

    >>> class Factory(object):
    ...     def __call__(self):
    ...         return Ob()
    ...     def getInterfaces(self):
    ...         return interface.implementedBy(Ob)

    >>> class ShortcutFactory(object):
    ...     interface.implements(interfaces.IShortcutFactory)
    ...     def __call__(self):
    ...         return Shortcut(Ob())
    ...     def getTargetInterfaces(self):
    ...         return interface.implementedBy(Ob)
    ...     def getInterfaces(self):
    ...         return interface.implementedBy(Shortcut)

    >>> factory = Factory()
    >>> shortcut_factory = ShortcutFactory()
    
    >>> def check(condition, container, name, obj, expected):
    ...     try:
    ...         condition(container, name, obj)
    ...     except InvalidItemType, v:
    ...         print v[0], (v[1] is obj or v[1]), (v[2] == expected or v[2])
    ...     else:
    ...         print 'Should have failed'
    ...
    >>> check(precondition, None, 'foo', ob, ())
    None True True
    >>> check(precondition.factory, None, 'foo', factory, ())
    None True True
    >>> check(types_precondition, None, 'foo', ob, (I1, I2))
    None True True
    >>> check(types_precondition.factory, None, 'foo', factory, (I1, I2))
    None True True
    >>> check(mixed_precondition, None, 'foo', ob, (I2,))
    None True True
    >>> check(mixed_precondition.factory, None, 'foo', factory, (I2,))
    None True True
    >>> check(precondition, None, 'foo', shortcut, (I1, I2))
    None True True
    >>> check(precondition.factory, None, 'foo', shortcut_factory, (I1, I2))
    None True True
    >>> check(types_precondition, None, 'foo', shortcut, ())
    None True True
    >>> check(types_precondition.factory, None, 'foo', shortcut_factory, ())
    None True True
    >>> check(mixed_precondition, None, 'foo', shortcut, (I2,))
    None True True
    >>> check(mixed_precondition.factory, None, 'foo', shortcut_factory, (I2,))
    None True True

    >>> interface.classImplements(Ob, I2)
    >>> precondition(None, 'foo', shortcut)
    >>> precondition.factory(None, 'foo', shortcut_factory)
    >>> types_precondition(None, 'foo', ob)
    >>> types_precondition.factory(None, 'foo', factory)
    >>> mixed_precondition(None, 'foo', shortcut)
    >>> mixed_precondition(None, 'foo', ob)
    >>> mixed_precondition.factory(None, 'foo', shortcut_factory)
    >>> mixed_precondition.factory(None, 'foo', factory)

    """

    interface.implements(interfaces.IShortcutTypePrecondition)

    def __init__(self, *target_types, **kwargs):
        self.target_types = target_types
        self.types = kwargs.pop('types', ())
        if kwargs:
            raise TypeError("ShortcutTypePrecondition.__init__ got an "
                            "unexpected keyword argument '%s'" % 
                            (kwargs.iterkeys().next(),))

    def __call__(self, container, name, object):
        if interfaces.IShortcut.providedBy(object):
            target = object.raw_target
            for iface in self.target_types:
                if iface.providedBy(target):
                    return
            raise InvalidItemType(container, object, self.target_types)
        else:
            for iface in self.types:
                if iface.providedBy(object):
                    return
            raise InvalidItemType(container, object, self.types)

    def factory(self, container, name, factory):
        if interfaces.IShortcutFactory.providedBy(factory):
            implemented = factory.getTargetInterfaces()
            for iface in self.target_types:
                if implemented.isOrExtends(iface):
                    return
            raise InvalidItemType(container, factory, self.target_types)
        else:
            implemented = factory.getInterfaces()
            for iface in self.types:
                if implemented.isOrExtends(iface):
                   return
            raise InvalidItemType(container, factory, self.types)


def contains(*types, **kwargs):
    """Declare that a container type contains only shortcuts to the given types

    This is used within a class suite defining an interface to create
    a __setitem__ specification with a precondition allowing only the
    given types:

      >>> class IFoo(interface.Interface):
      ...     pass
      >>> class IBar(interface.Interface):
      ...     pass
      >>> class IFooBarContainer(IContainer):
      ...     contains(IFoo, IBar)

      >>> __setitem__ = IFooBarContainer['__setitem__']
      >>> __setitem__.getTaggedValue('precondition').target_types == (
      ...     IFoo, IBar)
      True

    It is invalid to call contains outside a class suite:

      >>> contains(IFoo, IBar)
      Traceback (most recent call last):
      ...
      TypeError: contains not called from suite
    """

    frame = sys._getframe(1)
    f_locals = frame.f_locals
    f_globals = frame.f_globals
    
    if not (f_locals is not f_globals
            and f_locals.get('__module__')
            and f_locals.get('__module__') == f_globals.get('__name__')
            ):
        raise TypeError("contains not called from suite")

    def __setitem__(key, value):
        pass
    __setitem__.__doc__ = IContainer['__setitem__'].__doc__
    __setitem__.precondition = ShortcutTypePrecondition(*types, **kwargs)
    f_locals['__setitem__'] = __setitem__
