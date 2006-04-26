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

from zope.configuration.exceptions import ConfigurationError

from zope.generic.adapter.metaconfigure import adapterDirective
from zope.generic.factory.metaconfigure import factoryDirective
from zope.generic.informationprovider.metaconfigure import InformationProviderDirective

from zope.generic.type import ITypeInformation
from zope.generic.type import ITypeType



class TypeDirective(InformationProviderDirective):
    """Provide a new logical type."""

    # mark types with a type marker type
    _information_type = ITypeType


    def __init__(self, _context, keyface, label=None, hint=None):        
        # register types within the type information registry
        registry = ITypeInformation
        super(TypeDirective, self).__init__(_context, keyface, registry, label, hint)

    def factory(self, _context, class_, operations=(), input=None,
                providesKeyface=True, notifyCreated=False, storeInput=False):
        """Add factory."""
        factoryDirective(_context, self._keyface, class_, None, operations, input,
                     providesKeyface, notifyCreated, storeInput,
                     self._label, self._hint)


    def adapter(self, _context, provides, class_=None, writePermission=None, 
                readPermission=None, attributes=None, set_attributes=None, 
                key=None, informationProviders=None, acquire=False):
        """Provide a generic adatper for the key interface."""
        
        if informationProviders and acquire:
            raise ConfigurationError('Use informationsProviders or acquire attriubte.')

        if acquire:
            informationProviders = [ITypeInformation]

        adapterDirective(_context, provides, [self._keyface], class_, 
                     writePermission, readPermission, attributes,
                     set_attributes, key, informationProviders,)