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

$Id: meta.py,v 1.5 2002/09/16 05:52:40 rdmurray Exp $
"""


from INonEmptyDirective import INonEmptyDirective
from ISubdirectiveHandler import ISubdirectiveHandler


_directives = {}

class InvalidDirective(Exception):
    "An invalid directive was used"

class BrokenDirective(Exception):
    "A directive is implemented incorrectly"

def register(name, callable):
    """Register a top-level directive

    The name argument is a tuple with a namespace URI and an
    name string.

    The callable must be am IEmptyDirective or an INonEmptyDirective.

    INonEmptyDirective directives may have subdirectives. The
    subdirectives will be registered in a registry that is stored with
    the directive. The sub-directive registry is returned so that
    it can be used for subsequent sub-directive registration.

    """
    
    subdirs = {}
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
    directives. Rather, the handler is looked up as an attribute of
    the top-level directive object using the name string that is the
    second element in the name tuple.  An optional handler attribute
    can be used to specify the method to be used.

    Subdirectives may have subdirectives. The subdirectives will be
    registered in a registry that is stored with the containing
    subdirective. The sub-directive registry is returned so that it
    can be used for subsequent sub-directive registration.

    """
    if not handler_method:
        handler_method = name[1]
    subdirs = {}
    directives[name] = subdirs, handler_method
    return subdirs

def _exe(callable, subs, context, kw):
    r = callable(context, **kw)

    if subs or INonEmptyDirective.isImplementedBy(callable):
        return r, subs
    else:
        return (
            # We already have our list of actions, but we're expected to
            # provide a callable that returns one. 
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
            raise InvalidDirective(_name)

    return _exe(callable, subs, _context, kw)

def sub(subs, _name, _context, **kw):
    """Begin executing a subdirective

    The first argument, subs, is a registry of allowable subdirectives
    for the containing directive or subdirective.

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

    base, subdirs = subs
    try:
        subs = subdirs[_name]
    except KeyError:
        raise InvalidDirective(_name)
        
    # this is crufty.
    # if this is a tuple, it means we created it as such in 
    # registersub, and so we grab item 1 as the handler_method
    # and rebind subs as item 0
        
    if isinstance(subs, tuple):
        handler_method = subs[1]
        subs = subs[0]
    else:
        handler_method = _name[1]
    callable = getattr(base, handler_method)

    return _exe(callable, subs, _context, kw)

defaultkw = ({},)
def end(base):
    """Finish processing a directive or subdirective

    The argument is a return value from begin or sub.  Its first
    element is called to get a sequence of actions.

    The actions are normalized to a 4-element tuple with a
    descriminator, a callable, positional arguments, and keyword
    arguments. 
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

class DirectiveNamespace:

    def __init__(self, _context, namespace):
        self._namespace = namespace

    def directive(self, _context, name, handler, attributes='',
                  namespace=None):
        namespace = namespace or self._namespace
        subs = register((namespace, name), _context.resolve(handler))
        return Subdirective(subs, namespace=namespace)

    def __call__(self):
        return ()

def Directive(_context, namespace, name, handler, attributes=''):
    subs = register((namespace, name), _context.resolve(handler))
    return Subdirective(subs, namespace=namespace)

Directive.__implements__ = INonEmptyDirective

class InvaliDirectiveDefinition(Exception): pass

class Subdirective:
    """This is the meta-meta-directive"""
    # 
    # Unlike other directives, it doesn't return any actions, but
    # takes action right away, since it's actions are needed to process other
    # directives.
    # 
    # For this reason, this isn't a good directive example.

    __implements__ = ISubdirectiveHandler

    def __init__(self, subs, namespace=None):
        self._subs = subs
        self._namespace = namespace

    def subdirective(self, _context, name, attributes='',
                     namespace=None, handler_method=None):
        namespace = namespace or self._namespace
        if not namespace:
            raise InvaliDirectiveDefinition(name)
        #if not handler_method:
        #    handler_method = name
        subs = registersub(self._subs, (namespace, name), handler_method)
        return Subdirective(subs)

    def __call__(self):
        return ()

def _clear():
    "To support unit tests"
    _directives.clear()
    _directives[('http://namespaces.zope.org/zope', 'directive')] = (
        Directive, {
        ('http://namespaces.zope.org/zope', 'subdirective'): {
        ('http://namespaces.zope.org/zope', 'subdirective'): {
        ('http://namespaces.zope.org/zope', 'subdirective'): {
        }}}})
    _directives[('http://namespaces.zope.org/zope', 'directives')] = (
        DirectiveNamespace, {
        ('http://namespaces.zope.org/zope', 'directive'): {
        ('http://namespaces.zope.org/zope', 'subdirective'): {
        ('http://namespaces.zope.org/zope', 'subdirective'): {
        ('http://namespaces.zope.org/zope', 'subdirective'): {
        }}}}})

_clear()

# Register our cleanup with Testing.CleanUp to make writing unit tests simpler.
from Zope.Testing.CleanUp import addCleanUp
addCleanUp(_clear)
del addCleanUp
