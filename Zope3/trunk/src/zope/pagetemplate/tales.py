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
"""TALES

An implementation of a generic TALES engine
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

__version__ = '$Revision: 1.2 $'[11:-2]

import re
import sys
from types import StringTypes

from zope.pagetemplate import iterator
from zope.pagetemplate import safemapping

from zope.tal.interfaces import ITALESCompiler, ITALESEngine, ITALESErrorInfo


NAME_RE = r"[a-zA-Z][a-zA-Z0-9_]*"
_parse_expr = re.compile(r"(%s):" % NAME_RE).match
_valid_name = re.compile('%s$' % NAME_RE).match


class TALESError(Exception):
    """Error during TALES evaluation"""

class Undefined(TALESError):
    '''Exception raised on traversal of an undefined path'''

class CompilerError(Exception):
    '''TALES Compiler Error'''

class RegistrationError(Exception):
    '''Expression type or base name registration Error'''


_default = object()

_marker = object()


class Iterator(iterator.Iterator):
    def __init__(self, name, seq, context):
        iterator.Iterator.__init__(self, seq)
        self.name = name
        self._context = context

    def __iter__(self):
        return self

    def next(self):
        if iterator.Iterator.next(self):
            self._context.setLocal(self.name, self.seq[self.index])
            return 1
        return 0



class ErrorInfo:
    """Information about an exception passed to an on-error handler."""

    __implements__ = ITALESErrorInfo

    def __init__(self, err, position=(None, None)):
        if isinstance(err, Exception):
            self.type = err.__class__
            self.value = err
        else:
            self.type = err
            self.value = None
        self.lineno = position[0]
        self.offset = position[1]



class ExpressionEngine:
    '''Expression Engine

    An instance of this class keeps a mutable collection of expression
    type handlers.  It can compile expression strings by delegating to
    these handlers.  It can provide an expression Context, which is
    capable of holding state and evaluating compiled expressions.
    '''

    __implements__ = ITALESCompiler

    def __init__(self):
        self.types = {}
        self.base_names = {}
        self.iteratorFactory = Iterator

    def registerType(self, name, handler):
        if not _valid_name(name):
            raise RegistrationError, (
                'Invalid expression type name "%s".' % name)
        types = self.types
        if name in types:
            raise RegistrationError, (
                'Multiple registrations for Expression type "%s".' %
                name)
        types[name] = handler

    def getTypes(self):
        return self.types

    def registerBaseName(self, name, object):
        if not _valid_name(name):
            raise RegistrationError, 'Invalid base name "%s".' % name
        base_names = self.base_names
        if name in base_names:
            raise RegistrationError, (
                'Multiple registrations for base name "%s".' % name)
        base_names[name] = object

    def getBaseNames(self):
        return self.base_names

    def compile(self, expression):
        m = _parse_expr(expression)
        if m:
            type = m.group(1)
            expr = expression[m.end():]
        else:
            type = "standard"
            expr = expression
        try:
            handler = self.types[type]
        except KeyError:
            raise CompilerError, (
                'Unrecognized expression type "%s".' % type)
        return handler(type, expr, self)

    def getContext(self, contexts=None, **kwcontexts):
        if contexts is not None:
            if kwcontexts:
                kwcontexts.update(contexts)
            else:
                kwcontexts = contexts
        return Context(self, kwcontexts)

    def getCompilerError(self):
        return CompilerError


class Context:
    '''Expression Context

    An instance of this class holds context information that it can
    use to evaluate compiled expressions.
    '''

    __implements__ = ITALESEngine

    _context_class = safemapping.SafeMapping
    position = (None, None)
    source_file = None

    def __init__(self, engine, contexts):
        self._engine = engine
        self.contexts = contexts
        contexts['nothing'] = None
        contexts['default'] = _default

        self.repeat_vars = rv = {}
        # Wrap this, as it is visible to restricted code
        contexts['repeat'] = rep =  self._context_class(rv)
        contexts['loop'] = rep # alias

        self.global_vars = gv = contexts.copy()
        self.local_vars = lv = {}
        self.vars = self._context_class(gv, lv)

        # Keep track of what needs to be popped as each scope ends.
        self._scope_stack = []

    def beginScope(self):
        self._scope_stack.append([self.local_vars.copy()])

    def endScope(self):
        scope = self._scope_stack.pop()
        self.local_vars = lv = scope[0]
        v = self.vars
        v._pop()
        v._push(lv)
        # Pop repeat variables, if any
        i = len(scope) - 1
        while i:
            name, value = scope[i]
            if value is None:
                del self.repeat_vars[name]
            else:
                self.repeat_vars[name] = value
            i = i - 1

    def setLocal(self, name, value):
        self.local_vars[name] = value

    def setGlobal(self, name, value):
        self.global_vars[name] = value

    def setRepeat(self, name, expr):
        expr = self.evaluate(expr)
        if not expr:
            return self._engine.iteratorFactory(name, (), self)
        it = self._engine.iteratorFactory(name, expr, self)
        old_value = self.repeat_vars.get(name)
        self._scope_stack[-1].append((name, old_value))
        self.repeat_vars[name] = it
        return it

    def evaluate(self, expression,
                 isinstance=isinstance):
        if isinstance(expression, str):
            expression = self._engine.compile(expression)
        __traceback_supplement__ = (
            TALESTracebackSupplement, self, expression)
        return expression(self)

    evaluateValue = evaluate

    def evaluateBoolean(self, expr):
        return not not self.evaluate(expr)

    def evaluateText(self, expr):
        text = self.evaluate(expr)
        if text is _default or text is None:
            return text
        if not isinstance(text, StringTypes):
            text = unicode(text)
        return text

    def evaluateStructure(self, expr):
        return self.evaluate(expr)
    evaluateStructure = evaluate

    def evaluateMacro(self, expr):
        # XXX Should return None or a macro definition
        return self.evaluate(expr)
    evaluateMacro = evaluate

    def createErrorInfo(self, err, position):
        return ErrorInfo(err, position)

    def getDefault(self):
        return _default

    def setSourceFile(self, source_file):
        self.source_file = source_file

    def setPosition(self, position):
        self.position = position


class TALESTracebackSupplement:
    """Implementation of zope.exceptions.ITracebackSupplement"""
    def __init__(self, context, expression):
        self.context = context
        self.source_url = context.source_file
        self.line = context.position[0]
        self.column = context.position[1]
        self.expression = repr(expression)

    def getInfo(self, as_html=0):
        import pprint
        data = self.context.contexts.copy()
        if 'modules' in data:
            del data['modules']     # the list is really long and boring
        s = pprint.pformat(data)
        if not as_html:
            return '   - Names:\n      %s' % s.replace('\n', '\n      ')
        else:
            from cgi import escape
            return '<b>Names:</b><pre>%s</pre>' % (escape(s))
        return None



class SimpleExpr:
    '''Simple example of an expression type handler'''
    def __init__(self, name, expr, engine):
        self._name = name
        self._expr = expr
    def __call__(self, econtext):
        return self._name, self._expr
    def __repr__(self):
        return '<SimpleExpr %s %s>' % (self._name, `self._expr`)
