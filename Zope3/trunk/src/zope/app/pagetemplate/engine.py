##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Expression engine configuration and registration.

Each expression engine can have its own expression types and base names.

$Id: engine.py,v 1.11 2003/04/15 21:14:39 bwarsaw Exp $
"""
__metaclass__ = type # All classes are new style when run with Python 2.2+

import sys

from zope.tales.expressions import PathExpr
from zope.tales.expressions import StringExpr
from zope.tales.expressions import NotExpr
from zope.tales.expressions import DeferExpr
from zope.tales.pythonexpr import PythonExpr
from zope.tales.tales import ExpressionEngine
from zope.tales.tales import RegistrationError
from zope.tales.tales import Context

from zope.app.interfaces.traversing import ITraverser
from zope.app.traversing.adapters import Traverser
from zope.proxy.introspection import removeAllProxies
from zope.security.proxy import ProxyFactory
from zope.security.builtins import RestrictedBuiltins
from zope.i18n.translate import Translator

def zopeTraverser(object, path_items, econtext):
    """Traverses a sequence of names, first trying attributes then items.
    """
    traverser = Traverser(object)
    return traverser.traverse(path_items,
                              request=getattr(econtext, 'request', None))


class ZopePathExpr(PathExpr):

    def __init__(self, name, expr, engine):
        super(ZopePathExpr, self).__init__(name, expr, engine, zopeTraverser)

class ZopePythonExpr(PythonExpr):

    def __call__(self, econtext):
        __traceback_info__ = self.text
        vars = self._bind_used_names(econtext, RestrictedBuiltins)
        return eval(self._code, vars)

class ZopeContext(Context):

    def evaluateMacro(self, expr):
        macro = Context.evaluateMacro(self, expr)
        macro = removeAllProxies(macro)
        return macro

    # XXX msgid should come first, with domain defaulting to None.  When msgid
    # is a MessageID, domain tags along and needn't be specified.
    def translate(self, domain, msgid, mapping=None, default=None):
        # When running Zope, request is a Proxy, but no mutation is done here,
        # so it is safe to remove all proxies
        request = removeAllProxies(self.request)
        # XXX should we cache the translator instance?
        translator = Translator(request.locale, domain, self.context)
        return translator.translate(msgid, mapping, default=default)


class ZopeEngine(ExpressionEngine):

    def getContext(self, __namespace=None, **namespace):
        if __namespace:
            if namespace:
                namespace.update(__namespace)
            else:
                namespace = __namespace

        context = ZopeContext(self, namespace)

        # Put request into context so path traversal can find it
        if 'request' in namespace:
            context.request = namespace['request']

        # Put context into context so path traversal can find it
        # XXX: Change to container once the renaming has been done!
        if 'context' in namespace:
            context.context = namespace['context']

        return context

def Engine():
    e = ZopeEngine()
    for pt in ZopePathExpr._default_type_names:
        e.registerType(pt, ZopePathExpr)
    e.registerType('string', StringExpr)
    e.registerType('python', ZopePythonExpr)
    e.registerType('not', NotExpr)
    e.registerType('defer', DeferExpr)
    e.registerBaseName('modules', ProxyFactory(sys.modules))
    return e

Engine = Engine()

class AppPT:

    # Use our special engine
    pt_getEngineContext = Engine.getContext

    def pt_getEngine(self):
        return Engine
