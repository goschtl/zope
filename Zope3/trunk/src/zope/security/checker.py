##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""
$Id: checker.py,v 1.19 2003/04/23 18:18:02 stevea Exp $
"""

import os
import sys
import types
import datetime

from zope.i18n.messageid import MessageID
from zope.security.interfaces import IChecker
from zope.exceptions \
     import Unauthorized, ForbiddenAttribute, Forbidden, DuplicationError
from zope.interface.interfaces import IInterface
from zope.interface.implements import flattenInterfaces
from zope.interface import Interface
from zope.security._proxy import _Proxy as Proxy
from zope.security.interfaces import ISecurityProxyFactory
from zope.security.management import getSecurityManager

if os.environ.get('ZOPE_WATCH_CHECKERS'):
    WATCH_CHECKERS = True
else:
    WATCH_CHECKERS = False


def ProxyFactory(object, checker=None):
    """Factory function that creates a proxy for an object

    The proxy checker is looked up if not provided.
    """

    if checker is None:
        checker = getattr(object, '__Security_checker__', None)

    if checker is None:

        checker = selectChecker(object)
        if checker is None:
            return object

    else:
        # Maybe someone passed us a proxy and a checker
        if type(object) is Proxy:
            # XXX should we keep the existing proxy or create a new one.
            return object

    return Proxy(object, checker)

ProxyFactory.__implements__ = ISecurityProxyFactory

class Checker:

    __implements__ =  IChecker

    def __init__(self, permission_func,
                 setattr_permission_func=lambda name: None
                 ):
        """Create a checker

        A dictionary or a callable must be provided for computing
        permissions for names. The callable will be called with
        attribute names and must return a permission id, None, or the
        special marker, CheckerPublic. If None is returned, then
        access to the name is forbidden. If CheckerPublic is returned,
        then access will be granted without checking a permission.

        An optional setattr permission function or dictionary may be
        provided for checking set attribute access.
        """

        if type(permission_func) is dict:
            permission_func = permission_func.get
        self._permission_func = permission_func

        if type(setattr_permission_func) is dict:
            setattr_permission_func = setattr_permission_func.get
        self._setattr_permission_func = setattr_permission_func


    def getPermission_func(self):
        return self._permission_func

    def getSetattrPermission_func(self):
        return self._setattr_permission_func

    def permission_id(self, name):
        """Return the result of calling the permission func
        """
        return self._permission_func(name)

    def setattr_permission_id(self, name):
        """Return the result of calling the permission func
        """
        return self._setattr_permission_func(name)

    def check_getattr(self, object, name):
        'See IChecker'
        self.check(object, name)

    def check_setattr(self, object, name):
        'See IChecker'

        if WATCH_CHECKERS:
            print >> sys.stderr, ('Checking %r.%s:' % (object, name)),

        # We have the information we need already
        permission = self._setattr_permission_func(name)
        if permission:
            if permission is CheckerPublic:
                if WATCH_CHECKERS:
                    print >> sys.stderr, 'Public.'
                return # Public
            manager = getSecurityManager()
            if manager.checkPermission(permission, object):
                if WATCH_CHECKERS:
                    print >> sys.stderr, 'Granted.'
                return
            else:
                if WATCH_CHECKERS:
                    print >> sys.stderr, 'Unauthorized.'
                __traceback_supplement__ = (TracebackSupplement, object)
                raise Unauthorized(name=name)

        if WATCH_CHECKERS:
            print >> sys.stderr, 'Forbidden.'

        __traceback_supplement__ = (TracebackSupplement, object)
        raise ForbiddenAttribute(name)

    def check(self, object, name):
        'See IChecker'

        if WATCH_CHECKERS:
            print >> sys.stderr, ('Checking %r.%s:' % (object, name)),

        # We have the information we need already
        permission = self._permission_func(name)
        if permission:
            if permission is CheckerPublic:
                if WATCH_CHECKERS:
                    print >> sys.stderr, 'Public.'
                return # Public
            manager = getSecurityManager()
            if manager.checkPermission(permission, object):
                if WATCH_CHECKERS:
                    print >> sys.stderr, 'Granted.'
                return
            else:
                if WATCH_CHECKERS:
                    print >> sys.stderr, 'Unauthorized.'
                __traceback_supplement__ = (TracebackSupplement, object)
                raise Unauthorized(name=name)
        elif name in _always_available:
            if WATCH_CHECKERS:
                print >> sys.stderr, 'Always available.'
            return

        if WATCH_CHECKERS:
            print >> sys.stderr, 'Forbidden.'

        __traceback_supplement__ = (TracebackSupplement, object)
        raise ForbiddenAttribute(name)

    def proxy(self, value):
        'See IChecker'
        # Now we need to create a proxy

        checker = getattr(value, '__Security_checker__', None)
        if checker is None:
            checker = selectChecker(value)
            if checker is None:
                return value

        return Proxy(value, checker)

# Helper class for __traceback_supplement__
class TracebackSupplement:

    def __init__(self, obj):
        self.obj = obj

    def getInfo(self):
        result = []
        try:
            cls = self.obj.__class__
            if hasattr(cls, "__module__"):
                s = "%s.%s" % (cls.__module__, cls.__name__)
            else:
                s = str(cls.__name__)
            result.append("   - class: " + s)
        except:
            pass
        try:
            cls = type(self.obj)
            if hasattr(cls, "__module__"):
                s = "%s.%s" % (cls.__module__, cls.__name__)
            else:
                s = str(cls.__name__)
            result.append("   - type: " + s)
        except:
            pass
        return "\n".join(result)


# Marker for public attributes

# We want this to behave as a global, meaning it's pickled
# by name, rather than value. We need to arrange that it has a suitable
# __reduce__.
class Global(object):

    def __init__(self, name, module=None):
        if module is None:
            module = sys._getframe(1).f_locals['__name__']

        self.__name__ = name
        self.__module__ = module

    def __reduce__(self):
        return self.__name__

CheckerPublic = Global('CheckerPublic')

# Now we wrap it in a security proxy so that it retains it's
# identity when it needs to be security proxied.
d={}
CheckerPublic = Proxy(CheckerPublic, Checker(d))
d['__reduce__'] = CheckerPublic
del d

# XXX It's a bit scary above that we can pickle a proxy if access is
# granted to __reduce__. We might want to bother to prevent this in
# general and only allow it in this specific case.

def NamesChecker(names=(), permission_id=CheckerPublic, **__kw__):
    """Return a checker that grants access to a set of names.

    A sequence of names is given as the first argument. If a second
    argument, permission_id, is given, it is the permission required
    to access the names.  Additional names and persmission ids can be
    supplied as keyword arguments.
    """

    data = {}
    data.update(__kw__)
    for name in names:
        if data.get(name, permission_id) is not permission_id:
            raise DuplicationError(name)
        data[name] = permission_id

    return Checker(data.get)

def InterfaceChecker(interface, permission_id=CheckerPublic):
    return NamesChecker(interface.names(all=True), permission_id)

def MultiChecker(specs):
    """Create a checker from a sequence of specifications

    A specification is:

    - A two-tuple with:

      o a sequence of names or an interface

      o a permission id

      All the names in the sequence of names or the interface are
      protected by the permission.

    - A dictionoid (having an items method), with items that are
      name/permission-id pairs.
    """
    data = {}

    for spec in specs:
        if type(spec) is tuple:
            names, permission_id = spec
            if IInterface.isImplementedBy(names):
                names = names.names(all=True)
            for name in names:
                if data.get(name, permission_id) is not permission_id:
                    raise DuplicationError(name)
                data[name] = permission_id
        else:
            for name, permission_id in spec.items():
                if data.get(name, permission_id) is not permission_id:
                    raise DuplicationError(name)
                data[name] = permission_id

    return Checker(data.get)

def NonPrivateChecker(permission_id = CheckerPublic):

    def check(name, permission_id=permission_id):
        if name.startswith('_'):
            return None
        return permission_id

    return Checker(check)

def selectChecker(object):
    """Get a checker for the given object

    The appropriate checker is returned or None is returned. If the
    return value is None, then object should not be wrapped in a proxy.
    """

    # We need to be careful here. We might have a proxy, in which case
    # we can't use the type.  OTOH, we might not be able to use the
    # __class__ either, since not everything has one.

    # XXX we really need formal proxy introspection

    if type(object) is Proxy:
        # Is this already a security proxy?
        return None

    checker = _getChecker(getattr(object, '__class__', type(object)),
                          _defaultChecker)

    if checker is NoProxy:
        return None

    if checker is _defaultChecker and isinstance(object, Exception):
        return None

    while not isinstance(checker, Checker):
        checker = checker(object)
        if checker is NoProxy or checker is None:
            return None

    return checker

def getCheckerForInstancesOf(class_):
    return _checkers.get(class_)

def defineChecker(type_, checker):
    """Define a checker for a given type of object

    The checker can be a Checker, or a function that, when called with
    an object, returns a Checker.
    """
    if not isinstance(type_, (type, types.ClassType, types.ModuleType)):
        raise TypeError(
                'type_ must be a type, class or module, not a %s' % type_)
    if type_ in _checkers:
        raise DuplicationError(type_)
    _checkers[type_] = checker

NoProxy = object()

# _checkers is a mapping.
#
#  - Keys are types
#
#  - Values are
#
#    o None => rock
#    o a Checker
#    o a function returning None or a Checker
#
_checkers = {}
_getChecker = _checkers.get

_defaultChecker = Checker({}.get)

def _instanceChecker(inst):
    checker = _checkers.get(inst.__class__, _defaultChecker)
    if checker is _defaultChecker and isinstance(inst, Exception):
        return NoProxy # XXX we should be more careful
    return checker

def _classChecker(class_):
    # XXX This function does not appear to be used.
    #     What is it for?
    checker = _checkers.get(class_, _typeChecker)
    if checker is _typeChecker and issubclass(class_, Exception):
        return NoProxy # XXX we should be more careful

    return checker

def _moduleChecker(module):
    return _checkers.get(module, _typeChecker)



_always_available = ['__lt__', '__le__', '__eq__',
                     '__gt__', '__ge__', '__ne__',
                     '__hash__', '__nonzero__',
                     '__class__', '__implements__',
                     '__repr__'
                     ]

_callableChecker = NamesChecker(['__str__', '__name__', '__call__'])
_typeChecker = NamesChecker(
    ['__str__', '__name__', '__module__', '__bases__', '__mro__'])

_interfaceChecker = NamesChecker(['__str__', '__name__', '__module__',
                                  '__bases__', 'getBases', 'isImplementedBy',
                                  'extends'])

_iteratorChecker = NamesChecker(['next'])

BasicTypes = {
    object: NoProxy,
    int: NoProxy,
    float: NoProxy,
    long: NoProxy,
    complex: NoProxy,
    types.NoneType: NoProxy,
    str: NoProxy,
    unicode: NoProxy,
    type(True): NoProxy, # Boolean, if available :)
    datetime.timedelta: NoProxy,
    datetime.datetime: NoProxy,
    datetime.date: NoProxy,
    datetime.time: NoProxy,
}

class _Sequence(object):
    def __len__(self): return 0
    def __getitem__(self, i): raise IndexError

_default_checkers = {
    dict: NamesChecker(['__getitem__', '__len__', '__iter__',
                        'get', 'has_key', '__copy__', '__str__', 'keys',
                        'values', 'items', 'iterkeys', 'iteritems',
                        'itervalues', '__contains__']),
    list: NamesChecker(['__getitem__', '__getslice__', '__len__', '__iter__',
                        '__contains__', 'index', 'count', '__str__']),

    # YAGNI: () a rock
    tuple: NamesChecker(['__getitem__', '__getslice__', '__add__',
                         '__contains__', '__len__', '__iter__', '__iadd__',
                         '__str__']),
    types.InstanceType: _instanceChecker,
    Proxy: NoProxy,
    types.ClassType: _classChecker,
    types.FunctionType: _callableChecker,
    types.MethodType: _callableChecker,
    types.BuiltinFunctionType: _callableChecker,
    types.BuiltinMethodType: _callableChecker,
    type: _typeChecker,
    types.ModuleType: _moduleChecker,
    type(iter([])): _iteratorChecker, # Same types in Python 2.2.1,
    type(iter(())): _iteratorChecker, # different in Python 2.3.
    type(iter(_Sequence())): NamesChecker(['next']),
    type(Interface): _interfaceChecker,
}


def _clear():
    _checkers.clear()
    _checkers.update(_default_checkers)
    _checkers.update(BasicTypes)

_clear()

from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
