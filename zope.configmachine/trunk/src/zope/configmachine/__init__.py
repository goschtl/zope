##############################################################################
#
# Copyright (c) 2011 Zope Foundation and Contributors.
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
"""Configuration processor

"""

__docformat__ = 'restructuredtext'

import __builtin__
import os.path
import sys

from zope.interface.adapter import AdapterRegistry
from zope.interface import Interface
from zope.interface import implements
from zope.interface import providedBy

from zope.configmachine.exceptions import ConfigurationError
from zope.configmachine.exceptions import ConfigurationExecutionError
from zope.configmachine.exceptions import ConfigurationConflictError
from zope.configmachine.interfaces import IConfigurationContext
from zope.configmachine.interfaces import IGroupingContext

_import_chickens = {}, {}, ("*",) # dead chickens needed by __import__

class ConfigurationContext(object):
    """Mix-in that implements IConfigurationContext

    Subclasses provide a ``package`` attribute and a ``basepath``
    attribute.  If the base path is not None, relative paths are
    converted to absolute paths using the the base path. If the
    package is not none, relative imports are performed relative to
    the package.

    In general, the basepath and package attributes should be
    consistent. When a package is provided, the base path should be
    set to the path of the package directory.

    Subclasses also provide an ``actions`` attribute, which is a list
    of actions, an ``includepath`` attribute, and an ``info``
    attribute.

    The include path is appended to each action and is used when
    resolving conflicts among actions.  Normally, only the a
    ConfigurationMachine provides the actions attribute. Decorators
    simply use the actions of the context they decorate. The
    ``includepath`` attribute is a tuple of names.  Each name is
    typically the name of an included configuration file.

    The ``info`` attribute contains descriptive information helpful
    when reporting errors.  If not set, it defaults to an empty string.

    The actions attribute is a sequence of tuples with items:

      - discriminator, a value that identifies the action. Two actions
        that have the same (non None) discriminator conflict.

      - an object that is called to execute the action,

      - positional arguments for the action

      - keyword arguments for the action

      - a tuple of include file names (defaults to ())

      - an object that has descriptive information about
        the action (defaults to '')

    For brevity, trailing items after the callable in the tuples are
    ommitted if they are empty.

    """

    def __init__(self):
        super(ConfigurationContext, self).__init__()
        self._seen_files = set()
        self._features = set()

    def resolve(self, dottedname):
        """Resolve a dotted name to an object

        Examples:


        >>> c = ConfigurationContext()
        >>> import zope, zope.interface
        >>> c.resolve('zope') is zope
        1
        >>> c.resolve('zope.interface') is zope.interface
        1

        >>> c.resolve('zope.configmachine.eek') #doctest: +NORMALIZE_WHITESPACE
        Traceback (most recent call last):
        ...
        ConfigurationError:
        ImportError: Module zope.configmachine has no global eek

        >>> c.resolve('.ConfigurationContext')
        Traceback (most recent call last):
        ...
        AttributeError: 'ConfigurationContext' object has no attribute """ \
                                                                  """'package'
        >>> import zope.configmachine
        >>> c.package = zope.configmachine
        >>> c.resolve('.') is zope.configmachine
        1
        >>> c.resolve('.ConfigurationContext') is ConfigurationContext
        1
        >>> c.resolve('..interface') is zope.interface
        1
        >>> c.resolve('unicode')
        <type 'unicode'>
        """

        name = dottedname.strip()
        if not name:
            raise ValueError("The given name is blank")

        if name == '.':
            return self.package

        names = name.split('.')
        if not names[-1]:
            raise ValueError(
                "Trailing dots are no longer supported in dotted names")

        if len(names) == 1:
            # Check for built-in objects
            marker = object()
            obj = getattr(__builtin__, names[0], marker)
            if obj is not marker:
                return obj

        if not names[0]:
            # Got a relative name. Convert it to abs using package info
            if self.package is None:
                raise ConfigurationError(
                    "Can't use leading dots in dotted names, "
                    "no package has been set.")
            pnames = self.package.__name__.split(".")
            pnames.append('')
            while names and not names[0]:
                try:
                    names.pop(0)
                except IndexError:
                    raise ConfigurationError("Invalid global name", name)
                try:
                    pnames.pop()
                except IndexError:
                    raise ConfigurationError("Invalid global name", name)
            names[0:0] = pnames

        # Now we should have an absolute dotted name

        # Split off object name:
        oname, mname = names[-1], '.'.join(names[:-1])

        # Import the module
        if not mname:
            # Just got a single name. Must me a module
            mname = oname
            oname = ''

        try:
            mod = __import__(mname, *_import_chickens)
        except ImportError, v:
            if sys.exc_info()[2].tb_next is not None:
                # ImportError was caused deeper
                raise
            raise ConfigurationError(
                "ImportError: Couldn't import %s, %s" % (mname, v))

        if not oname:
            # see not mname case above
            return mod


        try:
            obj = getattr(mod, oname)
            return obj
        except AttributeError:
            # No such name, maybe it's a module that we still need to import
            try:
                return __import__(mname+'.'+oname, *_import_chickens)
            except ImportError:
                if sys.exc_info()[2].tb_next is not None:
                    # ImportError was caused deeper
                    raise
                raise ConfigurationError(
                    "ImportError: Module %s has no global %s" % (mname, oname))

    def path(self, filename):
        """
        Examples:

        >>> c = ConfigurationContext()
        >>> c.path("/x/y/z") == os.path.normpath("/x/y/z")
        1
        >>> c.path("y/z")
        Traceback (most recent call last):
        ...
        AttributeError: 'ConfigurationContext' object has no attribute """ \
                                                                 """'package'
        >>> import zope.configmachine
        >>> c.package = zope.configmachine
        >>> import os
        >>> d = os.path.dirname(zope.configmachine.__file__)
        >>> c.path("y/z") == d + os.path.normpath("/y/z")
        1
        >>> c.path("y/./z") == d + os.path.normpath("/y/z")
        1
        >>> c.path("y/../z") == d + os.path.normpath("/z")
        1
        """

        filename = os.path.normpath(filename)
        if os.path.isabs(filename):
            return filename

        # Got a relative path, combine with base path.
        # If we have no basepath, compute the base path from the package
        # path.

        basepath = getattr(self, 'basepath', '')

        if not basepath:
            if self.package is None:
                basepath = os.getcwd()
            else:
                if hasattr(self.package, '__path__'):
                    basepath = self.package.__path__[0]
                else:
                    basepath = os.path.dirname(self.package.__file__)
                basepath = os.path.abspath(basepath)
            self.basepath = basepath

        return os.path.join(basepath, filename)

    def checkDuplicate(self, filename):
        """Check for duplicate imports of the same file.

        Raises an exception if this file had been processed before.  This
        is better than an unlimited number of conflict errors.

        >>> c = ConfigurationContext()
        >>> c.checkDuplicate('/foo.zcml')
        >>> try:
        ...     c.checkDuplicate('/foo.zcml')
        ... except ConfigurationError, e:
        ...     # On Linux the exact msg has /foo, on Windows \foo.
        ...     str(e).endswith("foo.zcml' included more than once")
        True

        You may use different ways to refer to the same file:

        >>> import zope.configmachine
        >>> c.package = zope.configmachine
        >>> import os
        >>> d = os.path.dirname(zope.configmachine.__file__)
        >>> c.checkDuplicate('bar.zcml')
        >>> try:
        ...   c.checkDuplicate(d + os.path.normpath('/bar.zcml'))
        ... except ConfigurationError, e:
        ...   str(e).endswith("bar.zcml' included more than once")
        ...
        True

        """ #' <-- bow to font-lock
        path = self.path(filename)
        if path in self._seen_files:
            raise ConfigurationError('%r included more than once' % path)
        self._seen_files.add(path)

    def processFile(self, filename):
        """Check whether a file needs to be processed

        Return True if processing is needed and False otherwise. If
        the file needs to be processed, it will be marked as
        processed, assuming that the caller will procces the file if
        it needs to be procssed.

        >>> c = ConfigurationContext()
        >>> c.processFile('/foo.zcml')
        True
        >>> c.processFile('/foo.zcml')
        False

        You may use different ways to refer to the same file:

        >>> import zope.configmachine
        >>> c.package = zope.configmachine
        >>> import os
        >>> d = os.path.dirname(zope.configmachine.__file__)
        >>> c.processFile('bar.zcml')
        True
        >>> c.processFile('bar.zcml')
        False

        """ #' <-- bow to font-lock
        path = self.path(filename)
        if path in self._seen_files:
            return False
        self._seen_files.add(path)
        return True

    def action(self, discriminator, callable=None, args=(), kw={}, order=0,
               includepath=None, info=None):
        """Add an action with the given discriminator, callable and arguments

        For testing purposes, the callable and arguments may be omitted.
        In that case, a default noop callable is used.

        The discriminator must be given, but it can be None, to indicate that
        the action never conflicts.

        Let's look at some examples:

        >>> c = ConfigurationContext()

        Normally, the context gets actions from subclasses. We'll provide
        an actions attribute ourselves:

        >>> c.actions = []

        We'll use a test callable that has a convenient string representation

        >>> from zope.configmachine.tests.directives import f

        >>> c.action(1, f, (1, ), {'x': 1})
        >>> c.actions
        [(1, f, (1,), {'x': 1})]

        >>> c.action(None)
        >>> c.actions
        [(1, f, (1,), {'x': 1}), (None, None)]

        Now set the include path and info:

        >>> c.includepath = ('foo.zcml',)
        >>> c.info = "?"
        >>> c.action(None)
        >>> c.actions[-1]
        (None, None, (), {}, ('foo.zcml',), '?')

        We can add an order argument to crudely control the order
        of execution:

        >>> c.action(None, order=99999)
        >>> c.actions[-1]
        (None, None, (), {}, ('foo.zcml',), '?', 99999)

        We can also pass an includepath argument, which will be used as the the
        includepath for the action.  (if includepath is None, self.includepath
        will be used):

        >>> c.action(None, includepath=('abc',))
        >>> c.actions[-1]
        (None, None, (), {}, ('abc',), '?')

        We can also pass an info argument, which will be used as the the
        source line info for the action.  (if info is None, self.info will be
        used):

        >>> c.action(None, info='abc')
        >>> c.actions[-1]
        (None, None, (), {}, ('foo.zcml',), 'abc')
        
        """
        if info is None:
            info = getattr(self, 'info', '')

        if includepath is None:
            includepath = getattr(self, 'includepath', ())
            
        action = (discriminator, callable, args, kw, includepath, info, order)

        # remove trailing false items
        while (len(action) > 2) and not action[-1]:
            action = action[:-1]

        self.actions.append(action)

    def hasFeature(self, feature):
        """Check whether a named feature has been provided.

        Initially no features are provided

        >>> c = ConfigurationContext()
        >>> c.hasFeature('onlinehelp')
        False

        You can declare that a feature is provided

        >>> c.provideFeature('onlinehelp')

        and it becomes available

        >>> c.hasFeature('onlinehelp')
        True

        """
        return feature in self._features

    def provideFeature(self, feature):
        """Declare thata named feature has been provided.

        See `hasFeature` for examples.
        """
        self._features.add(feature)


class ConfigurationAdapterRegistry(object):
    """Simple adapter registry that manages directives as adapters

    >>> r = ConfigurationAdapterRegistry()
    >>> c = ConfigurationMachine()
    >>> r.factory(c, ('http://www.zope.com','xxx'))
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Unknown directive', 'http://www.zope.com', 'xxx')
    >>> from zope.configmachine.interfaces import IConfigurationContext
    >>> def f():
    ...     pass

    >>> r.register(IConfigurationContext, ('http://www.zope.com', 'xxx'), f)
    >>> r.factory(c, ('http://www.zope.com','xxx')) is f
    1
    >>> r.factory(c, ('http://www.zope.com','yyy')) is f
    Traceback (most recent call last):
    ...
    ConfigurationError: ('Unknown directive', 'http://www.zope.com', 'yyy')
    >>> r.register(IConfigurationContext, 'yyy', f)
    >>> r.factory(c, ('http://www.zope.com','yyy')) is f
    1
    >>> class IFullInfo(Interface): pass

    Test the documentation feature:

    >>> r._docRegistry
    []
    >>> r.document(('ns', 'dir'), IFullInfo, IConfigurationContext, None,
    ...            'inf', None)
    >>> r._docRegistry[0][0] == ('ns', 'dir')
    1
    >>> r._docRegistry[0][1] is IFullInfo
    1
    >>> r._docRegistry[0][2] is IConfigurationContext
    1
    >>> r._docRegistry[0][3] is None
    1
    >>> r._docRegistry[0][4] == 'inf'
    1
    >>> r._docRegistry[0][5] is None
    1
    >>> r.document('all-dir', None, None, None, None)
    >>> r._docRegistry[1][0]
    ('', 'all-dir')
    """


    def __init__(self):
        super(ConfigurationAdapterRegistry, self).__init__()
        self._registry = {}
        # Stores tuples of form:
        #   (namespace, name), schema, usedIn, info, parent
        self._docRegistry = []

    def register(self, interface, name, factory):
        r = self._registry.get(name)
        if r is None:
            r = AdapterRegistry()
            self._registry[name] = r

        r.register([interface], Interface, '', factory)

    def document(self, name, schema, usedIn, handler, info, parent=None):
        if isinstance(name, (str, unicode)):
            name = ('', name)
        self._docRegistry.append((name, schema, usedIn, handler, info, parent))

    def factory(self, context, name):
        r = self._registry.get(name)
        if r is None:
            # Try namespace-independent name
            ns, n = name
            r = self._registry.get(n)
            if r is None:
                raise ConfigurationError("Unknown directive", ns, n)

        f = r.lookup1(providedBy(context), Interface)
        if f is None:
            raise ConfigurationError(
                "The directive %s cannot be used in this context" % (name, ))
        return f

class ConfigurationMachine(ConfigurationAdapterRegistry, ConfigurationContext):
    """Configuration machine

    Example usage can be found in the ``zope.configuration`` unit tests.
    """

    implements(IConfigurationContext)

    package = None
    basepath = None
    includepath = ()
    info = ''

    def __init__(self):
        super(ConfigurationMachine, self).__init__()
        self.actions = []
        self.stack = [RootStackItem(self)]
        self.i18n_strings = {}

    def begin(self, __name, __data=None, __info=None, **kw):
        if __data:
            if kw:
                raise TypeError("Can't provide a mapping object and keyword "
                                "arguments")
        else:
            __data = kw
        self.stack.append(self.stack[-1].contained(__name, __data, __info))

    def end(self):
        self.stack.pop().finish()

    def __call__(self, __name, __info=None, **__kw):
        self.begin(__name, __kw, __info)
        self.end()

    def getInfo(self):
        return self.stack[-1].context.info

    def setInfo(self, info):
        self.stack[-1].context.info = info

    def execute_actions(self, clear=True, testing=False):
        """Execute the configuration actions

        This calls the action callables after resolving conflicts

        For example:

        >>> output = []
        >>> def f(*a, **k):
        ...    output.append(('f', a, k))
        >>> context = ConfigurationMachine()
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   ]
        >>> context.execute_actions()
        >>> output
        [('f', (1,), {}), ('f', (2,), {})]

        If the action raises an error, we convert it to a
        ConfigurationExecutionError.

        >>> output = []
        >>> def bad():
        ...    bad.xxx
        >>> context.actions = [
        ...   (1, f, (1,)),
        ...   (1, f, (11,), {}, ('x', )),
        ...   (2, f, (2,)),
        ...   (3, bad, (), {}, (), 'oops')
        ...   ]
        >>> try:
        ...    v = context.execute_actions()
        ... except ConfigurationExecutionError, v:
        ...    pass
        >>> print v
        exceptions.AttributeError: 'function' object has no attribute 'xxx'
          in:
          oops


        Note that actions executed before the error still have an effect:

        >>> output
        [('f', (1,), {}), ('f', (2,), {})]


        """
        try:
            for action in resolveConflicts(self.actions):
                (discriminator, callable, args, kw, includepath, info, order
                 ) = expand_action(*action)
                if callable is None:
                    continue
                try:
                    callable(*args, **kw)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except:
                    if testing:
                        raise
                    t, v, tb = sys.exc_info()
                    raise ConfigurationExecutionError(t, v, info), None, tb
        finally:
            if clear:
                del self.actions[:]


##############################################################################
# Stack items

class RootStackItem(object):

    def __init__(self, context):
        self.context = context

    def contained(self, name, data, info):
        """Handle a contained directive

        We have to compute a new stack item by getting a named adapter
        for the current context object.

        """
        factory = self.context.factory(self.context, name)
        if factory is None:
            raise ConfigurationError("Invalid directive", name)
        adapter = factory(self.context, data, info)
        return adapter

    def finish(self):
        pass

##############################################################################
# Helper classes

class GroupingContextDecorator(ConfigurationContext):
    """Helper mix-in class for building grouping directives

    See the discussion (and test) in GroupingStackItem.
    """

    implements(IConfigurationContext, IGroupingContext)

    def __init__(self, context, **kw):
        self.context = context
        for name, v in kw.items():
            setattr(self, name, v)

    def __getattr__(self, name,
                    getattr=getattr, setattr=setattr):
        v = getattr(self.context, name)
        # cache result in self
        setattr(self, name, v)
        return v

    def before(self):
        pass

    def after(self):
        pass

##############################################################################
# Conflict resolution

def expand_action(discriminator, callable=None, args=(), kw={},
                   includepath=(), info='', order=0):
    return (discriminator, callable, args, kw,
            includepath, info, order)

def resolveConflicts(actions):
    """Resolve conflicting actions

    Given an actions list, identify and try to resolve conflicting actions.
    Actions conflict if they have the same non-null discriminator.
    Conflicting actions can be resolved if the include path of one of
    the actions is a prefix of the includepaths of the other
    conflicting actions and is unequal to the include paths in the
    other conflicting actions.

    Here are some examples to illustrate how this works:

    >>> from zope.configmachine.tests.directives import f
    >>> from pprint import PrettyPrinter
    >>> pprint=PrettyPrinter(width=60).pprint
    >>> pprint(resolveConflicts([
    ...    (None, f),
    ...    (1, f, (1,), {}, (), 'first'),
    ...    (1, f, (2,), {}, ('x',), 'second'),
    ...    (1, f, (3,), {}, ('y',), 'third'),
    ...    (4, f, (4,), {}, ('y',), 'should be last', 99999),
    ...    (3, f, (3,), {}, ('y',)),
    ...    (None, f, (5,), {}, ('y',)),
    ... ]))
    [(None, f),
     (1, f, (1,), {}, (), 'first'),
     (3, f, (3,), {}, ('y',)),
     (None, f, (5,), {}, ('y',)),
     (4, f, (4,), {}, ('y',), 'should be last')]

    >>> try:
    ...     v = resolveConflicts([
    ...        (None, f),
    ...        (1, f, (2,), {}, ('x',), 'eek'),
    ...        (1, f, (3,), {}, ('y',), 'ack'),
    ...        (4, f, (4,), {}, ('y',)),
    ...        (3, f, (3,), {}, ('y',)),
    ...        (None, f, (5,), {}, ('y',)),
    ...     ])
    ... except ConfigurationConflictError, v:
    ...    pass
    >>> print v
    Conflicting configuration actions
      For: 1
        eek
        ack

    """

    # organize actions by discriminators
    unique = {}
    output = []
    for i in range(len(actions)):
        (discriminator, callable, args, kw, includepath, info, order
         ) = expand_action(*(actions[i]))

        order = order or i
        if discriminator is None:
            # The discriminator is None, so this directive can
            # never conflict. We can add it directly to the
            # configuration actions.
            output.append(
                (order, discriminator, callable, args, kw, includepath, info)
                )
            continue


        a = unique.setdefault(discriminator, [])
        a.append(
            (includepath, order, callable, args, kw, info)
            )

    # Check for conflicts
    conflicts = {}
    for discriminator, dups in unique.items():

        # We need to sort the actions by the paths so that the shortest
        # path with a given prefix comes first:
        dups.sort()
        (basepath, i, callable, args, kw, baseinfo) = dups[0]
        output.append(
            (i, discriminator, callable, args, kw, basepath, baseinfo)
            )
        for includepath, i, callable, args, kw, info in dups[1:]:
            # Test whether path is a prefix of opath
            if (includepath[:len(basepath)] != basepath # not a prefix
                or
                (includepath == basepath)
                ):
                if discriminator not in conflicts:
                    conflicts[discriminator] = [baseinfo]
                conflicts[discriminator].append(info)


    if conflicts:
        raise ConfigurationConflictError(conflicts)

    # Now put the output back in the original order, and return it:
    output.sort()
    r = []
    for o in output:
        action = o[1:]
        while len(action) > 2 and not action[-1]:
            action = action[:-1]
        r.append(action)

    return r

