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
$Id: metametaconfigure.py,v 1.6 2003/05/01 19:35:39 faassen Exp $
"""
from zope.interface import directlyProvides
from zope.configuration.meta \
     import DirectiveNamespace as bootstrapDirectiveNamespace
from zope.configuration.meta import Subdirective as bootstrapSubdirective
from zope.configuration.interfaces import INonEmptyDirective
from zope.configuration.interfaces import ISubdirectiveHandler

#
# Meta-meta configuration.  These routines replace the bootstrap ones
# defined in meta.py.
#

class DirectiveNamespace(bootstrapDirectiveNamespace):

    __class_implements_ = INonEmptyDirective
    __implements__ = ISubdirectiveHandler

    def _Subdirective(self, *args, **kw):
        return Subdirective(*args, **kw)

    def _useDescription(self, namespace, name, handler, description, subs):
        pass

    def directive(self, _context, name, handler, attributes='',
                  namespace=None, description=''):

        subs, namespace = self._register(_context, name, handler, namespace)

        # Extra whitespace is not significant, since the parser
        # removes the newlines.
        description = ' '.join(description.strip().split())

        self._useDescription(namespace, name, handler, description, subs)

        return self._Subdirective(subs, namespace=namespace, name=name)

    directlyProvides(directive, INonEmptyDirective)


class Subdirective(bootstrapSubdirective):
    """An extended Subdirective that handles descriptions and attributes"""

    __implements__ = ISubdirectiveHandler

    def __init__(self, subs, namespace=None, name=None):
        bootstrapSubdirective.__init__(self,subs,namespace)
        self._name = name

    def _useDescription(self, namespace, name, subs, description):
        pass

    def subdirective(self, _context, name, attributes='',
                     namespace=None, handler_method=None, description=''):

        subs, namespace = self._register(_context, name, namespace,
                                         handler_method)

        # Extra whitespace is not significant, since the parser
        # removes the newlines.
        description = ' '.join(description.strip().split())

        self._useDescription(namespace, name, subs, description)
        return self.__class__(subs, namespace=namespace, name=name)

    directlyProvides(subdirective, INonEmptyDirective)

    def _useAttributeDescription(self, name, required, description):
        pass

    def attribute(self, _context, name, required='', description=''):
        return Attribute(self, name, required, description)

    directlyProvides(attribute, INonEmptyDirective)

    def description(self, _context):
        return Description(self)

    directlyProvides(description, INonEmptyDirective)

class Description:

    __implements__ = ISubdirectiveHandler
    
    def __init__(self, dir):
        self._dir = dir
        self._description = ''

    def zcmlText(self, text):
        self._description += text

    def __call__(self):
        self._dir._useDescription(
            self._dir._namespace, self._dir._name, self._dir._subs,
            self._description)

        return ()

class Attribute:

    __implements__ = ISubdirectiveHandler
    
    def __init__(self, dir, name, required, description=''):
        required = required.lower()
        if required not in ('', 'yes', 'no'):
            raise ValueError(required)

        # Extra whitespace is not significant, since the parser
        # removes the newlines.
        description = ' '.join(description.strip().split())

        self._dir = dir
        self._name = name
        self._required = required
        self._description = description

    def description(self, _context):
        return AttrDescription(self)

    directlyProvides(description, INonEmptyDirective)

    def __call__(self):
        self._dir._useAttributeDescription(
            self._name, self._required, self._description)
        return ()

class AttrDescription:

    __implements__ = ISubdirectiveHandler
    
    def __init__(self, dir):
        self._dir = dir

    def zcmlText(self, text):
        self._dir._description += text

    def __call__(self):
        return ()
        
