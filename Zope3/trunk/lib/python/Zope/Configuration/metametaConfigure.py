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
"""
$Id: metametaConfigure.py,v 1.3 2002/11/08 19:08:27 rdmurray Exp $
"""
from meta import DirectiveNamespace as bootstrapDirectiveNamespace
from meta import Subdirective as bootstrapSubdirective
from INonEmptyDirective import INonEmptyDirective
from IEmptyDirective import IEmptyDirective
from ISubdirectiveHandler import ISubdirectiveHandler

#
# Meta-meta configuration.  These routines replace the bootstrap ones
# defined in meta.py.
#

class DirectiveNamespace(bootstrapDirectiveNamespace):

    __class_implements_ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    def _Subdirective(self, *args, **kw): return Subdirective(*args, **kw)

    def _useDescription(self, namespace, name, handler, description, subs): pass

    def directive(self, _context, name, handler, attributes='',
            namespace=None, description=''):
        subs, namespace = self._register(_context, name, handler, namespace)
        self._useDescription(namespace, name, handler, description, subs)
        return self._Subdirective(subs, namespace=namespace, name=name)
    directive.__implements__ = INonEmptyDirective


class Subdirective(bootstrapSubdirective):
    """An extended Subdirective that handles descriptions and attributes"""

    __implements__ = ISubdirectiveHandler

    def __init__(self, subs, namespace=None, name=None):
        bootstrapSubdirective.__init__(self,subs,namespace)
        self._name = name

    def _useDescription(self, namespace, name, subs, description): pass

    def subdirective(self, _context, name, attributes='',
                     namespace=None, handler_method=None, description=''):
        subs, namespace = self._register(_context, name, namespace,
                                         handler_method)
        self._useDescription(namespace, name, subs, description)
        return self.__class__(subs, namespace=namespace, name=name)
    subdirective.__implements__ = INonEmptyDirective

    def _useAttributeDescription(self, name, required, description): pass

    def attribute(self, _context, name, required='', description=''):
        required = required.lower()
        if required not in ('', 'yes', 'no'): raise ValueError(required)
        self._useAttributeDescription(name, required, description)
        return ()
    attribute.__implements__ = IEmptyDirective
