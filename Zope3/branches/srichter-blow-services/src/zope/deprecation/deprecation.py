##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Deprecation Support

This module provides utilities to ease the development of backward-compatible
code.

$Id$
"""
__docformat__ = "reStructuredText"
import sys
import types
import warnings
import zope.proxy

class DeprecationProxy(zope.proxy.ProxyBase):

    def __init__(self, module):
        super(DeprecationProxy, self).__init__(module)
        self._deprecated = {}

    def deprecate(self, names, message):
        """Deprecate the given names."""
        if not isinstance(names, (tuple, list)):
            names = (names,)
        for name in names:
            self._deprecated[name] = message

    def __getattribute__(self, name):
        if name != '_deprecated' and name in self._deprecated:
            warnings.warn(self._deprecated[name], DeprecationWarning, 2)

        return super(DeprecationProxy, self).__getattribute__(name)


class DeprecatedGetProperty(object):

    def __init__(self, prop, message):
        self.message = message
        self.prop = prop

    def __get__(self, inst, klass):
        warnings.warn(self.message, DeprecationWarning, 2)
        return self.prop.__get__(inst, klass)

class DeprecatedGetSetProperty(DeprecatedGetProperty):

    def __set__(self, inst, prop):
        warnings.warn(self.message, DeprecationWarning, 2)
        self.prop.__set__(inst, prop)

class DeprecatedGetSetDeleteProperty(DeprecatedGetSetProperty):

    def __delete__(self, inst):
        warnings.warn(self.message, DeprecationWarning, 2)
        self.prop.__delete__(inst)

def DeprecatedMethod(method, message):

    def deprecated_method(self, *args, **kw):
        warnings.warn(message, DeprecationWarning, 2)
        return method(self, *args, **kw)

    return deprecated_method


def deprecated(specifier, message):
    """Deprecate the given names."""

    # We are inside a module
    if isinstance(specifier, (str, unicode, list, tuple)):
        locals = sys._getframe(1).f_locals
        if '__name__' in locals:
            modname = locals['__name__']
            
        if not isinstance(sys.modules[modname], DeprecationProxy):
            sys.modules[modname] = DeprecationProxy(sys.modules[modname])
        sys.modules[modname].deprecate(specifier, message)
        

    # ... that means the specifier is a method or attribute of the class
    if isinstance(specifier, types.FunctionType):
        return DeprecatedMethod(specifier, message)
    else:
        prop = specifier
        if hasattr(prop, '__get__') and hasattr(prop, '__set__') and \
               hasattr(prop, '__delete__'):
            return DeprecatedGetSetDeleteProperty(prop, message)
        elif hasattr(prop, '__get__') and hasattr(prop, '__set__'):
            return DeprecatedGetSetProperty(prop, message)
        elif hasattr(prop, '__get__'):
            return DeprecatedGetProperty(prop, message)

    
