##############################################################################
#
# Copyright (c) 2005, 2006 Zope Corporation and Contributors.
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

"""
$Id$
"""

__docformat__ = 'restructuredtext'

from zope.component.interface import provideInterface
from zope.configuration.exceptions import ConfigurationError
from zope.interface import alsoProvides

from zope.generic.adapter.metaconfigure import adapterDirective
from zope.generic.face import IConfaceType
from zope.generic.face import IKeyfaceType
from zope.generic.factory.metaconfigure import factoryDirective
from zope.generic.handler.metaconfigure import handlerDirective
from zope.generic.informationprovider.metaconfigure import ensureInformationProvider
from zope.generic.operation import INoParameter

from zope.generic.face import IUndefinedContext



class ContentDirective(object):
    """Provide a new logical type."""

    # mark types with a type marker type
    _information_type = IUndefinedContext


    def __init__(self, _context, keyface, label=None, hint=None):        
        # register types within the type information registry
        if IConfaceType.providedBy(keyface):
            raise ConfigurationError('Key interface %s can not be registered '
                                     'as context interface too.' % 
                                     keyface.__name__)

        # assign variables for the subdirecitives
        self._keyface = keyface
        self._context = _context
        self._conface = conface = IUndefinedContext

        # provide type as soon as possilbe
        if not IKeyfaceType.providedBy(keyface):
            provideInterface(None, keyface, IKeyfaceType)

        if not IConfaceType.providedBy(conface):
            provideInterface(None, conface, IConfaceType)

        # ensure the corresponding information provider
        ensureInformationProvider(keyface, conface)

    def factory(self, _context, class_, operations=(), input=INoParameter,
                providesFace=True, notifyCreated=False, storeInput=False):
        """Add factory."""
        factoryDirective(_context, self._keyface, class_, operations, input,
                     providesFace, notifyCreated, storeInput)


    def adapter(self, _context, provides, class_=None, writePermission=None, 
                readPermission=None, attributes=None, set_attributes=None, 
                key=None, informationProviders=None, acquire=False):
        """Provide a generic adatper for the key interface."""
        
        if informationProviders and acquire:
            raise ConfigurationError('Use informationsProviders or acquire attriubte.')

        if acquire:
            informationProviders = [IUndefinedContext]

        adapterDirective(_context, provides, [self._keyface], class_, 
                     writePermission, readPermission, attributes,
                     set_attributes, key, informationProviders,)

    def handler(self, _context, event, operations=(), input=None):
        """Provide a object event handler."""
        handlerDirective(_context, self._keyface, event, operations, input)
