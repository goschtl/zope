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
"""Registration of registration directives

See IEmptyDirective, INonEmptyDirective, and ISubdirectiveHandler.

$Id: meta.py,v 1.3 2002/12/28 00:02:29 jim Exp $
"""


from zope.interfaces.configuration import INonEmptyDirective
from zope.interfaces.configuration import ISubdirectiveHandler

class InvalidDirective(Exception):
    """An invalid directive was used"""

class BrokenDirective(Exception):
    """A directive is implemented incorrectly"""

class InvalidDirectiveDefinition(Exception):
    """The definition of a directive is incomplete or incorrect"""


#
# Registry data structure and manipulation functions.
#

# _directives is a registry that holds information on zcml directives
# and subdirectives.  It is filled by the 'directives', 'directive' and
# 'subdirective' directives that are provided as the bootstrap
# directives by the _clear function of this module.
#
# The top level of the registry is a dictionary keyed by two element
# tuples.  Each key tuple consists of a namespace designator (such as
# http://namespaces.zope.org/zope) and a directive name.  Thus, the
# key that accesses the 'directive' directive is::
#
#     (http://namespaces.zope.org/zope', 'directive')
#
# The value of a directive entry is a two element tuple consisting
# of a callable and a (possibly empty) subdirective registry.  The
# callable is the object to be called to process the directive and
# its parameters.  The callable must be either an IEmptyDirective (in
# which case the subdirective registry should be empty), or an
# INonEmptyDirective (in which case there should be one or more entries
# in the subdirective registry).
#
# A subdirective registry is also keyed by (ns, name) tuples.  Handler
# methods for subdirectives are looked up on the ISubdirectiveHandler
# object that is returned by the INonEmptyDirective that handles
# the directive to which the subdirective registry belongs.
# INonEmptyDirective objects are thus most often classes.
#
# The value of an entry in the subdirective registry is a tuple of
# two elements.  The first element is a subdirective registry, and
# the second is the name to be looked up to find the callable that
# will handle the processing of the subdirective.  That callable
# should implement either IEmtpyDirective or INonEmptyDirective.  The
# accompanying sub-subdirective registry should be empty or not,
# accordingly.

_directives = {}

def register(name, callable):
    """Register a top-level directive

    The name argument is a tuple with a namespace URI and an
    name string.

    The callable must be am IEmptyDirective or an INonEmptyDirective.

    INonEmptyDirective directives may have subdirectives. The
    subdirectives will be registered in a registry that is stored with
    the directive. The sub-directive registry is returned so that
    it can be used for subsequent sub-directive registration.

    If the same name is registered a second time, the existing
    subdirective registry will be returned.

    """

    subdirs = _directives.get(name,(None,{}))[1]
    _directives[name] = callable, subdirs
    return subdirs

def registersub(directives, name, handler_method=None):
    """Register a subdirective

    directives is the subdirective registry for the containing
    directive, which may be either a top-level directive or an
    intermediate sub-directive (if subdirectives are nested more than
    two deep).

    The name argument is a tuple with a namespace URI and an
    name string.

    The handler is not passed as it normally is for top-level
    directives. Rather, the handler will be looked up as an attribute
    of the ISubdirectiveHandler returned by INonEmptyDirective whose
    associated registry we have been passed.  The string to be
    looked up is set to the second element of the name tuple, unless
    the optional handler attribute is used to provide the lookup
    string explicitly.

    Subdirectives may have subdirectives. The subdirectives will be
    registered in a registry that is stored with the containing
    subdirective. The sub-directive registry is returned so that it
    can be used for subsequent sub-directive registration.

    If the same name is registered a second time, the existing
    subdirective registry will be returned.

    """
    if not handler_method:
        handler_method = name[1]
    subdirs = directives.get(name,({},))[0]
    directives[name] = subdirs, handler_method
    return subdirs

#
# Parser handler methods.  These methods are called by the code that
# parses configuration data to process the directives and subdirectives.
# 'begin' is called to start processing a directive.  Its return
# value should be saved.  When the directive is closed (which will
# be right away for IEmptyDirectives), that saved return value is
# passed to end, which will return a list of actions to append to
# the action list.  Nested subdirectives are processed similarly,
# except that 'sub' is called to start them rather than begin, and
# the first argument passed to sub should be the tuple returned
# by begin (or sub) for the enclosing (sub)directive (it will be
# an ISubdirectiveHandler, subdirectiveregistry pair).  The
# end result will be a list of actions.  See IEmptyDirective for a
# description of the actions data structure.
#

def _exe(callable, subs, context, kw):
    """Helper function to turn an IxxxDirective into a (callable, subs) tuple
    """

    # We've either got an IEmptyDirective or an INonEmptyDirective here.
    # For the former, we're going to get back a list of actions when
    # we call it.  For the latter, we're going to get back an
    # ISubdirectiveHandler.  We need to return something that end
    # can call the first element of to get a list of actions.
    # ISubdirectiveHandler qualifies, but we'll have to manufacture
    # one if we got a list of actions.  When we return the
    # ISubdirectiveHandler, the parsing code calling begin/sub is
    # going to pass the tuple along to sub in order to process the
    # subdirectives.

    r = callable(context, **kw)

    if INonEmptyDirective.isImplementedBy(callable):
        return r, subs
    else:
        return (
            (lambda: r),
            subs,
            )

def begin(_custom_directives, _name, _context, **kw):
    """Begin executing a top-level directive

    A custom registry is provided to provide specialized directive
    handlers in addition to the globally registered directives. For
    example, the XML configuration mechanism uses these to provide XML
    configuration file directives.

    The _name argument is a tuple with a namespace URI and a
    name string.

    The _context argument is an execution context object that
    directives use for functions like resolving names. It will be
    passed as the first argument to the directive handler.

    kw are the directive arguments.

    The return value is a tuple that contains:

    - An object to be called to finish directive processing. This
      object will return a sequence of actions. The object must be
      called after sub-directives are processed.

    - A registry for looking up subdirectives.

    """

    if _custom_directives and (_name in _custom_directives):
        callable, subs = _custom_directives[_name]
    else:
        try:
            callable, subs = _directives[_name]
        except KeyError:
            # Maybe the directive is a multi-namespace directive
            # (like include)
            try:
                if _custom_directives:
                    callable, subs = _custom_directives[('*', _name[1])]
                else:
                    raise InvalidDirective(_name)
                
            except KeyError:
                raise InvalidDirective(_name)

    return _exe(callable, subs, _context, kw)

def sub(handlertuple, _name, _context, **kw):
    """Begin executing a subdirective

    The first argument, handlertuple, is a pair consisting of
    an ISubdirectiveHandler and a registry of allowable subdirectives
    for the containing directive or subdirective.

    The _name argument is a tuple with a namespace URI and a
    name string, naming the subdirective we are executing.

    The _context argument is an execution context object that
    directives use for functions like resolving names. It will be
    passed as the first argument to the directive handler.

    kw are the directive arguments.

    The return value is a tuple that contains:

    - An object to be called to finish directive processing. This
      object will return a sequence of actions. The object must be
      called after sub-directives are processed.

    - A registry for looking up sub-subdirectives.

    """

    base, subdirs = handlertuple
    try:
        subsubs, handler_method = subdirs[_name]
    except KeyError:
        raise InvalidDirective(_name)

    callable = getattr(base, handler_method)

    return _exe(callable, subsubs, _context, kw)

defaultkw = ({},)
def end(base):
    """Finish processing a directive or subdirective

    The argument is a return value from begin or sub.  Its first
    element is called to get a sequence of actions.

    The return value is a list of actions that are normalized to a
    4-element tuple with a descriminator, a callable, positional
    arguments, and keyword arguments.
    """

    actions = base[0]()
    ractions = []
    for action in actions:
        if len(action) < 3 or len(action) > 4:
            raise BrokenDirective(action)
        if len(action) == 3:
            action += defaultkw
        ractions.append(action)
    return ractions


#
# The code below provides the implementation for the directives,
# directive, and subdirective handlers.  These will be called
# via begin and sub when the code parsing a (meta) configuration
# file encounters these directives.  The association between
# the directive names and the particular callables is set up
# in _clear.
#

class DirectiveNamespace:

    __class_implements__ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    def __init__(self, _context, namespace):
        self._namespace = namespace

    def _register(self, _context, name, handler, namespace=None,
                  attributes=''):
        namespace = namespace or self._namespace
        subs = register((namespace, name), _context.resolve(handler))
        return subs, namespace

    def directive(self, *args, **kw):
        subs, namespace = self._register(*args, **kw)
        return Subdirective(subs, namespace=namespace)
    directive.__implements__ = INonEmptyDirective

    def __call__(self):
        return ()


class Subdirective:
    """This is the meta-meta-directive"""
    #
    # Unlike other directives, it doesn't return any actions, but
    # takes action right away, since its actions are needed to process other
    # directives.
    #
    # For this reason, this isn't a good directive example.

    __implements__ = ISubdirectiveHandler

    def __init__(self, subs, namespace=None):
        self._subs = subs
        self._namespace = namespace

    def _register(self, _context, name, namespace=None, handler_method=None,
                  attributes=''):
        namespace = namespace or self._namespace
        if not namespace:
            raise InvalidDirectiveDefinition(name)
        #If handler_method is None, registersub will use name.
        subs = registersub(self._subs, (namespace, name), handler_method)
        return subs, namespace

    def subdirective(self, *args, **kw):
        subs, namespace = self._register(*args, **kw)
        return Subdirective(subs,namespace=namespace)
    subdirective.__implements__ = INonEmptyDirective

    def __call__(self):
        return ()

def _clear():
    """Initialize _directives data structure with bootstrap directives."""

    # We initialize _directives with handlers for three (sub)directives:
    # directives, directive, and subdirective.  Given these three
    # (whose implementation is contained in this module) we can use
    # zcml to define any other directives needed for a given system.
    #
    # The data structure created here is recursive.  This allows for
    # an unlimited number of levels of subdirective definition
    # nesting.
    #
    # This initialziation is done in a function to facilitate support
    # the unittest CleanUp class.

    _directives.clear()
    zopens = 'http://namespaces.zope.org/zope'
    subdirkey = (zopens, 'subdirective')
    subs = {}
    subs[subdirkey] = (subs, 'subdirective')
    directive = {(zopens, 'directive'): (subs, 'directive')}
    _directives[(zopens, 'directives')] = (DirectiveNamespace, directive)

_clear()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from zope.testing.cleanup import addCleanUp
addCleanUp(_clear)
del addCleanUp
