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
"""Javascript Form Framework AJAX Framework.

$Id: $
"""
__docformat__ = "reStructuredText"
import sys
import zope.component
import zope.interface
from zope.publisher.interfaces import NotFound
from zope.publisher.browser import BrowserPage
from z3c.traverser import traverser
from z3c.form.util import SelectionManager
from z3c.traverser.interfaces import ITraverserPlugin
from z3c.formjs import util, interfaces


class AJAXHandlers(SelectionManager):
    """A selection manager for handling AJAX request handlers."""

    def addHandler(self, name, handler):
        self._data_keys.append(name)
        self._data_values.append(handler)
        self._data[name] = handler

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.keys())


class AJAXHandler(object):
    zope.interface.implements(interfaces.IAJAXHandler)

    def __init__(self, func):
        self.func = func

    def __call__(self, view):
        return self.func(view)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.func.__name__)


class AJAXRequestHandler(object):
    """Mix-in class for forms to support AJAX calls."""
    zope.interface.implements(interfaces.IAJAXRequestHandler,
                              interfaces.IFormTraverser)

    ajaxRequestHandlers = AJAXHandlers()


def handler(func):
    """A decorator for defining an AJAX request handler."""
    handler = AJAXHandler(func)
    frame = sys._getframe(1)
    f_locals = frame.f_locals
    handlers = f_locals.setdefault('ajaxRequestHandlers', AJAXHandlers())
    handlers.addHandler(func.__name__, handler)
    return handler


class AJAXView(BrowserPage):
    """A wrapper class around AJAX handler to allow it to be publishable."""

    def __init__(self, handler, request, view):
        self.context = self.handler = handler
        self.request = request
        self.__parent__ = self.view = view

    def __call__(self):
        return self.handler(self.view)


class AJAXRequestTraverserPlugin(object):
    """Allow access to methods registered as an ajax request handler."""

    zope.interface.implements(ITraverserPlugin)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def publishTraverse(self, request, name):
        handler = self.context.ajaxRequestHandlers.get(name)
        if handler is None:
            raise NotFound(self.context, name, request)

        return AJAXView(handler, self.request, self.context)
