##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""Javascript Functions.

$Id$
"""
__docformat__ = "reStructuredText"
import cStringIO
import compiler
import inspect
import sys
import zope.component
import zope.interface
from zope.viewlet import viewlet
from zope.publisher.interfaces.browser import IBrowserRequest

from z3c.formjs import interfaces

class JSFunction(object):
    zope.interface.implements(interfaces.IJSFunction)

    def __init__(self, namespace, function):
        self.namespace = namespace
        self.function = function

    @property
    def name(self):
        return self.function.func_name

    @property
    def arguments(self):
        args = inspect.getargspec(self.function)[0]
        if args[0] is 'self':
            del args[0]
        return args

    def render(self):
        return self.function(*[x for x in ['self'] + self.arguments])

    def call(self, *args):
        sargs = []
        for arg in args:
            argtype = type(arg)
            if argtype is unicode:
                sargs.append(repr(arg)[1:])
            elif argtype is bool:
                sargs.append(repr(arg).lower())
            elif argtype in (int, float, str):
                sargs.append(repr(arg))
            else:
                sargs.append(repr(str(arg)))
        caller = self.name
        if self.namespace:
            caller = '%s.%s' % (self.namespace, self.name)
        return '%s(%s);' % (caller, ','.join(sargs))

    def __repr__(self):
        return '<%s %s>' % (
            self.__class__.__name__, self.name)


class JSFunctions(object):
    zope.interface.implements(interfaces.IJSFunctions)

    def __init__(self):
        self._functions = {}

    def add(self, jsFunction, namespace=''):
        ns = self._functions.setdefault(namespace, [])
        ns.append(jsFunction)
        return jsFunction

    def render(self):
        result = ''
        # Render non-namespaced functions
        for func in self._functions.get('', []):
            args = func.arguments
            result += 'function %s(%s) {\n' %(
                func.name, ', '.join(args) )
            code = func.render()
            result += '  ' + code.replace('\n', '\n  ') + '\n'
            result += '}\n'
        # Render namespaced functions
        for ns, funcs in self._functions.items():
            if ns == '':
                continue
            result += 'var %s = {\n' %ns
            for func in funcs:
                args = func.arguments
                result += '  %s: function(%s) {\n' %(
                    func.name, ', '.join(args) )
                code = func.render()
                result += '    ' + code.replace('\n', '\n    ') + '\n'
                result += '  },\n'
            result = result[:-2] + '\n'
            result += '}\n'
        return result

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self._functions)

def function(namespace=''):
    """A decorator for defining a javascript function."""
    def createFunction(func):
        frame = sys._getframe(1)
        f_locals = frame.f_locals
        funcs = f_locals.setdefault('jsFunctions', JSFunctions())
        jsFunction = JSFunction(namespace, func)
        return funcs.add(jsFunction, namespace)
    return createFunction


class JSFunctionsViewlet(viewlet.ViewletBase):
    """An viewlet for the JS viewlet manager rendering functions."""
    zope.component.adapts(
        zope.interface.Interface,
        IBrowserRequest,
        interfaces.IHaveJSFunctions,
        zope.interface.Interface)

    def render(self):
        content = self.__parent__.jsFunctions.render()
        return u'<script type="text/javascript">\n%s\n</script>' % content
