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
"""Security Checkers

You can set the environment variable ZOPE_WATCH_CHECKERS to get additional
security checker debugging output on the standard error.

Setting ZOPE_WATCH_CHECKERS to 1 will display messages about unauthorized or
forbidden attribute access.  Setting it to a larger number will also display
messages about granted attribute access.

Note that the ZOPE_WATCH_CHECKERS mechanism will eventually be
replaces with a more general ecurity auditing mechanism.

$Id$
"""
import os
import sys
import types
import datetime
import weakref
import zope.interface.interface
import zope.interface.interfaces

from zope.interface import directlyProvides, Interface, implements
from zope.interface.interfaces import IInterface, IDeclaration
from zope.interface.declarations import ProvidesClass
from zope.interface.declarations import Implements
from zope.interface.declarations import Declaration
from zope.security.interfaces import IChecker, INameBasedChecker
from zope.security.interfaces import ISecurityProxyFactory
from zope.security.management import getSecurityPolicy, queryInteraction
from zope.security._proxy import _Proxy as Proxy, getChecker
from zope.exceptions import Unauthorized, ForbiddenAttribute, DuplicationError

__metaclass__ = type

if os.environ.get('ZOPE_WATCH_CHECKERS'):
    try:
        WATCH_CHECKERS = int(os.environ.get('ZOPE_WATCH_CHECKERS'))
    except ValueError:
        WATCH_CHECKERS = 1
else:
    WATCH_CHECKERS = 0


def ProxyFactory(object, checker=None):
    """Factory function that creates a proxy for an object

    The proxy checker is looked up if not provided.
    """
    if type(object) is Proxy:
        if checker is None or checker is getChecker(object):
            return object
        else:
            # We have a proxy, but someone asked us to change its checker.
            # Let's raise an exception.
            #
            # Other reasonable actions would be to either keep the existing
            # proxy, or to create a new one with the given checker.
            # The latter might be a security hole though, if untrusted code
            # can call ProxyFactory.
            raise TypeError("Tried to use ProxyFactory to change a Proxy's"
                            " checker.")
    if checker is None:
        checker = getattr(object, '__Security_checker__', None)

        if checker is None:
            checker = selectChecker(object)
            if checker is None:
                return object
    else:
        c = getattr(object, '__Security_checker__', None)
        if c is not None:
            pass
            # XXX This is odd. We're being asked to use a checker that is
            #     not the "natural" one for this object.
    return Proxy(object, checker)

directlyProvides(ProxyFactory, ISecurityProxyFactory)


class TrustedCheckerBase:
    """Marker type used by zope.security.proxy.trustedRemoveSecurityProxy"""


class Checker(TrustedCheckerBase):
    implements(INameBasedChecker)

    def __init__(self, get_permissions, set_permissions=None):
        """Create a checker

        A dictionary must be provided for computing permissions for
        names. The disctionary get will be called with attribute names
        and must return a permission id, None, or the special marker,
        CheckerPublic. If None is returned, then access to the name is
        forbidden. If CheckerPublic is returned, then access will be
        granted without checking a permission.

        An optional setattr dictionary may be provided for checking
        set attribute access.

        """

        assert isinstance(get_permissions, dict)
        self.get_permissions = get_permissions
        if set_permissions is not None:
            assert isinstance(set_permissions, dict)
        self.set_permissions = set_permissions

    def permission_id(self, name):
        'See INameBasedChecker'
        return self.get_permissions.get(name)

    def setattr_permission_id(self, name):
        'See INameBasedChecker'
        if self.set_permissions:
            return self.set_permissions.get(name)

    def check_getattr(self, object, name):
        'See IChecker'
        self.check(object, name)

    def check_setattr(self, object, name):
        'See IChecker'
        if self.set_permissions:
            permission = self.set_permissions.get(name)
        else:
            permission = None
            
        if permission is not None:
            if permission is CheckerPublic:
                return # Public
            policy = getSecurityPolicy()
            interaction = queryInteraction()
            if policy.checkPermission(permission, object, interaction):
                return
            else:
                __traceback_supplement__ = (TracebackSupplement, object)
                raise Unauthorized, name

        __traceback_supplement__ = (TracebackSupplement, object)
        raise ForbiddenAttribute, (name, object)

    def check(self, object, name):
        'See IChecker'
        permission = self.get_permissions.get(name)
        if permission is not None:
            if permission is CheckerPublic:
                return # Public
            policy = getSecurityPolicy()
            interaction = queryInteraction()
            if policy.checkPermission(permission, object, interaction):
                return
            else:
                __traceback_supplement__ = (TracebackSupplement, object)
                raise Unauthorized, name
        elif name in _always_available:
            return

        if name != '__iter__' or hasattr(object, name):
            __traceback_supplement__ = (TracebackSupplement, object)
            raise ForbiddenAttribute, (name, object)

    def proxy(self, value):
        'See IChecker'
        checker = getattr(value, '__Security_checker__', None)
        if checker is None:
            checker = selectChecker(value)
            if checker is None:
                return value

        return Proxy(value, checker)


class CombinedChecker(Checker):
    """A checker that combines two other checkers in a logical-or fashion.

    The following table describes the result of a combined checker in detail.

    checker1           checker2           CombinedChecker(checker1, checker2)
    ------------------ ------------------ -----------------------------------
    ok                 anything           ok (checker2 is never called)
    Unauthorized       ok                 ok
    Unauthorized       Unauthorized       Unauthorized
    Unauthorized       ForbiddenAttribute Unauthorized
    ForbiddenAttribute ok                 ok
    ForbiddenAttribute Unauthorized       Unauthorized
    ForbiddenAttribute ForbiddenAttribute ForbiddenAttribute
    ------------------ ------------------ -----------------------------------
    """
    implements(IChecker)

    def __init__(self, checker1, checker2):
        """Create a combined checker."""
        Checker.__init__(self,
                         checker1.get_permissions,
                         checker1.set_permissions)
        self._checker2 = checker2

    def check(self, object, name):
        'See IChecker'
        try:
            Checker.check(self, object, name)
        except ForbiddenAttribute:
            self._checker2.check(object, name)
        except Unauthorized, unauthorized_exception:
            try: self._checker2.check(object, name)
            except ForbiddenAttribute:
                raise unauthorized_exception

    def check_getattr(self, object, name):
        'See IChecker'
        try:
            Checker.check_getattr(self, object, name)
        except ForbiddenAttribute:
            self._checker2.check_getattr(object, name)
        except Unauthorized, unauthorized_exception:
            try: self._checker2.check_getattr(object, name)
            except ForbiddenAttribute:
                raise unauthorized_exception

    def check_setattr(self, object, name):
        'See IChecker'
        try:
            Checker.check_setattr(self, object, name)
        except ForbiddenAttribute:
            self._checker2.check_setattr(object, name)
        except Unauthorized, unauthorized_exception:
            try: self._checker2.check_setattr(object, name)
            except ForbiddenAttribute:
                raise unauthorized_exception

class CheckerLoggingMixin:
    """Debugging mixin for checkers.

    Prints verbose debugging information about every performed check to
    sys.stderr.

    If verbosity is set to 1, only displays Unauthorized and Forbidden messages.
    If verbosity is set to a larger number, displays all messages.
    """

    verbosity = 1

    def check(self, object, name):
        try:
            super(CheckerLoggingMixin, self).check(object, name)
            if self.verbosity > 1:
                if name in _always_available:
                    print >> sys.stderr, (
                        '[CHK] + Always available: %s on %r' % (name, object))
                else:
                    print >> sys.stderr, (
                        '[CHK] + Granted: %s on %r' % (name, object))
        except Unauthorized:
            print >> sys.stderr, (
                '[CHK] - Unauthorized: %s on %r' % (name, object))
            raise
        except ForbiddenAttribute:
            print >> sys.stderr, (
                '[CHK] - Forbidden: %s on %r' % (name, object))
            raise

    def check_getattr(self, object, name):
        try:
            super(CheckerLoggingMixin, self).check(object, name)
            if self.verbosity > 1:
                if name in _always_available:
                    print >> sys.stderr, (
                        '[CHK] + Always available getattr: %s on %r'
                        % (name, object))
                else:
                    print >> sys.stderr, (
                        '[CHK] + Granted getattr: %s on %r'
                        % (name, object))
        except Unauthorized:
            print >> sys.stderr, (
                '[CHK] - Unauthorized getattr: %s on %r' % (name, object))
            raise
        except ForbiddenAttribute:
            print >> sys.stderr, (
                '[CHK] - Forbidden getattr: %s on %r' % (name, object))
            raise

    def check_setattr(self, object, name):
        try:
            super(CheckerLoggingMixin, self).check_setattr(object, name)
            if self.verbosity > 1:
                print >> sys.stderr, (
                    '[CHK] + Granted setattr: %s on %r' % (name, object))
        except Unauthorized:
            print >> sys.stderr, (
                '[CHK] - Unauthorized setattr: %s on %r' % (name, object))
            raise
        except ForbiddenAttribute:
            print >> sys.stderr, (
                '[CHK] - Forbidden setattr: %s on %r' % (name, object))
            raise


if WATCH_CHECKERS:
    class Checker(CheckerLoggingMixin, Checker):
        verbosity = WATCH_CHECKERS
    class CombinedChecker(CheckerLoggingMixin, CombinedChecker):
        verbosity = WATCH_CHECKERS


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


class Global(object):
    """A global object that behaves like a string.

    We want this to behave as a global, meaning it's pickled
    by name, rather than value. We need to arrange that it has a suitable
    __reduce__.
    """

    def __init__(self, name, module=None):
        if module is None:
            module = sys._getframe(1).f_locals['__name__']

        self.__name__ = name
        self.__module__ = module

    def __reduce__(self):
        return self.__name__

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__,
                              self.__name__, self.__module__)

# Marker for public attributes
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
    to access the names.  Additional names and permission ids can be
    supplied as keyword arguments.
    """

    data = {}
    data.update(__kw__)
    for name in names:
        if data.get(name, permission_id) is not permission_id:
            raise DuplicationError(name)
        data[name] = permission_id

    return Checker(data)

def InterfaceChecker(interface, permission_id=CheckerPublic, **__kw__):
    return NamesChecker(interface.names(all=True), permission_id, **__kw__)

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
            if IInterface.providedBy(names):
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

    return Checker(data)

def selectChecker(object):
    """Get a checker for the given object

    The appropriate checker is returned or None is returned. If the
    return value is None, then object should not be wrapped in a proxy.
    """

    # We need to be careful here. We might have a proxy, in which case
    # we can't use the type.  OTOH, we might not be able to use the
    # __class__ either, since not everything has one.

    # XXX we really need formal proxy introspection

    #if type(object) is Proxy:
    #    # Is this already a security proxy?
    #    return None

    checker = _getChecker(type(object), _defaultChecker)

    #checker = _getChecker(getattr(object, '__class__', type(object)),
    #                      _defaultChecker)

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

# Get optimized versions
try:
    import zope.security._zope_security_checker
except ImportError:
    pass
else:
    from zope.security._zope_security_checker import _checkers, selectChecker
    from zope.security._zope_security_checker import NoProxy

_getChecker = _checkers.get

_defaultChecker = Checker({})

def _instanceChecker(inst):
    checker = _checkers.get(inst.__class__, _defaultChecker)
    if checker is _defaultChecker and isinstance(inst, Exception):
        return NoProxy # XXX we should be more careful
    return checker

def _classChecker(class_):
    if issubclass(class_, Exception):
        return NoProxy  # XXX we should be more careful

    return _typeChecker

def moduleChecker(module):
    return _checkers.get(module)


# The variable '_always_available' should really be called
# '_available_by_default', as that would better reflect its meaning.
# XXX: Fix the name.
_always_available = ['__lt__', '__le__', '__eq__',
                     '__gt__', '__ge__', '__ne__',
                     '__hash__', '__nonzero__',
                     '__class__', '__providedBy__', '__implements__',
                     '__repr__', '__conform__',
                     ]

_callableChecker = NamesChecker(['__str__', '__name__', '__call__'])
_typeChecker = NamesChecker(
    ['__str__', '__name__', '__module__', '__bases__', '__mro__'])
_namedChecker = NamesChecker(['__name__'])

_iteratorChecker = NamesChecker(['next', '__iter__'])

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

# Available for tests. Located here so it can be kept in sync with BasicTypes.
BasicTypes_examples = {
    object: object(),
    int: 65536,
    float: -1.4142,
    long: 65536l,
    complex: -1.4142j,
    types.NoneType: None,
    str: 'abc',
    unicode: u'uabc',
    type(True): True,
    datetime.timedelta: datetime.timedelta(3),
    datetime.datetime: datetime.datetime(2003, 1, 1),
    datetime.date: datetime.date(2003, 1, 1),
    datetime.time: datetime.time(23, 58)
}


class _Sequence(object):
    def __len__(self): return 0
    def __getitem__(self, i): raise IndexError

_Declaration_checker = InterfaceChecker(
    IDeclaration,
    _implied=CheckerPublic,
    subscribe=CheckerPublic)

def f():
    yield f


_default_checkers = {
    dict: NamesChecker(['__getitem__', '__len__', '__iter__',
                        'get', 'has_key', 'copy', '__str__', 'keys',
                        'values', 'items', 'iterkeys', 'iteritems',
                        'itervalues', '__contains__']),
    list: NamesChecker(['__getitem__', '__getslice__', '__len__', '__iter__',
                        '__contains__', 'index', 'count', '__str__',
                        '__add__', '__radd__', ]),

    # YAGNI: () a rock
    tuple: NamesChecker(['__getitem__', '__getslice__', '__add__', '__radd__',
                         '__contains__', '__len__', '__iter__',
                         '__str__']),
    types.InstanceType: _instanceChecker,
    Proxy: NoProxy,
    type(weakref.ref(_Sequence())): NamesChecker(['__call__']),
    types.ClassType: _classChecker,
    types.FunctionType: _callableChecker,
    types.MethodType: _callableChecker,
    types.BuiltinFunctionType: _callableChecker,
    types.BuiltinMethodType: _callableChecker,
    type(().__getslice__): _callableChecker, # slot description
    type: _typeChecker,
    types.ModuleType: lambda module: _checkers.get(module, _namedChecker),
    type(iter([])): _iteratorChecker, # Same types in Python 2.2.1,
    type(iter(())): _iteratorChecker, # different in Python 2.3.
    type(iter({})): _iteratorChecker,
    type(iter(_Sequence())): _iteratorChecker,
    type(f()): _iteratorChecker,
    type(Interface): InterfaceChecker(
        IInterface,
        __str__=CheckerPublic, _implied=CheckerPublic, subscribe=CheckerPublic,
        # XXX Backward:
        isImplementedByInstancesOf=CheckerPublic,
        isImplementedBy=CheckerPublic,
        ),
    zope.interface.interface.Method: InterfaceChecker(
                                        zope.interface.interfaces.IMethod),
    ProvidesClass: _Declaration_checker,
    Implements: _Declaration_checker,
    Declaration: _Declaration_checker,
}

def _clear():
    _checkers.clear()
    _checkers.update(_default_checkers)
    _checkers.update(BasicTypes)

_clear()

from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
