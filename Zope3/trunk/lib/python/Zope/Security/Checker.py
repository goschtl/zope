from Zope.Security.IChecker import IChecker
from Zope.Exceptions \
     import Unauthorized, ForbiddenAttribute, Forbidden, DuplicationError
from Interface.IInterface import IInterface
from Interface import Interface
from _Proxy import _Proxy as Proxy
from ISecurityProxyFactory import ISecurityProxyFactory
from Zope.Security.SecurityManagement import getSecurityManager
import sys, os, types

if os.environ.get('ZOPE_WATCH_CHECKERS'):
    WATCH_CHECKERS = 1
else:
    WATCH_CHECKERS = 0


# Marker for public attributes
CheckerPublic = object()

def ProxyFactory(object, checker=None):
    """Factory function that creats a proxy for an object

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

    ############################################################
    # Implementation methods for interface
    # Zope.Security.IChecker.

    def check_getattr(self, object, name):
        'See Zope.Security.IChecker.IChecker'
        self.check(object, name)

    def check_setattr(self, object, name):
        'See Zope.Security.IChecker.IChecker'

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
                raise Unauthorized(name=name)

        if WATCH_CHECKERS:
            print >> sys.stderr, 'Forbidden.'

        raise ForbiddenAttribute(name)

    def check(self, object, name):
        'See Zope.Security.IChecker.IChecker'

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
                raise Unauthorized(name=name)
        elif name in _always_available:
            if WATCH_CHECKERS:
                print >> sys.stderr, 'Always available.'
            return

        if WATCH_CHECKERS:
            print >> sys.stderr, 'Forbidden.'

        raise ForbiddenAttribute(name)

    def proxy(self, value):
        'See Zope.Security.IChecker.IChecker'
        # Now we need to create a proxy

        checker = getattr(value, '__Security_checker__', None)
        if checker is None:
            checker = selectChecker(value)
            if checker is None:
                return value

        return Proxy(value, checker)

    #
    ############################################################

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
    return NamesChecker(interface.names(1), permission_id)

def MultiChecker(specs):
    """Create a checker from a sequence of specifications

    A specification is:

    - A two-tuple with:

      o a sequence of names or an interface

      o a permission id

      All the names in the sequence of names or the interface are
      protected by the permission.

    - A dictionoid (having anitems method), with items that are
      name/permission-id pairs.
    """
    data = {}

    for spec in specs:
        if type(spec) is tuple:
            names, permission_id = spec
            if IInterface.isImplementedBy(names):
                names = names.names(1)
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
    checker = _getChecker(type(object), _defaultChecker)
    if checker is NoProxy:
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
                     ]

_callableChecker = NamesChecker(['__str__', '__repr__', '__name__',
                                 '__call__'])
_typeChecker = NamesChecker(['__str__', '__repr__', '__name__', '__module__',
                             '__bases__'])

_interfaceChecker = NamesChecker(['__str__', '__repr__', '__name__',
                                  '__module__', '__bases__', 'getBases',
                                  'isImplementedBy', 'extends'])

BasicTypes = {
    object: NoProxy,
    int: NoProxy,
    float: NoProxy,
    long: NoProxy,
    complex: NoProxy,
    types.NoneType: NoProxy,
    str: NoProxy,
    unicode: NoProxy,
    type(not 1): NoProxy, # Boolean, if available :)
}

class _Sequence(object):
    def __len__(self): return 0
    def __getitem__(self, i): raise IndexError

_default_checkers = {
    dict: NamesChecker(['__getitem__', '__len__', '__iter__',
                        'get', 'has_key', '__copy__',
                        'keys', 'values', 'items',
                        'iterkeys', 'iteritems', 'itervalues', '__contains__',
                        ]),
    list: NamesChecker(['__getitem__', '__getslice__', '__len__', '__iter__',
                        '__contains__', 'index', 'count']),

    # YAGNI: () a rock
    tuple: NamesChecker(['__getitem__', '__getslice__', '__add__',
                         '__contains__', '__len__', '__iter__', '__iadd__']),
    types.InstanceType: _instanceChecker,
    Proxy: NoProxy,
    types.ClassType: _classChecker,
    types.FunctionType: _callableChecker,
    types.MethodType: _callableChecker,
    types.BuiltinFunctionType: _callableChecker,
    types.BuiltinMethodType: _callableChecker,
    type: _typeChecker,
    types.ModuleType: _moduleChecker,
    type(iter([])): NamesChecker(['next']), # same types in Python 2.2.1,
    type(iter(())): NamesChecker(['next']), # different in Python 2.3
    type(iter(_Sequence())): NamesChecker(['next']),
    type(Interface): _interfaceChecker,
    }


def _clear():
    _checkers.clear()
    _checkers.update(_default_checkers)
    _checkers.update(BasicTypes)

_clear()

from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
