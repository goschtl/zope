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

from zope.app.component.contentdirective import ClassDirective
from zope.component.zcml import adapter
from zope.configuration.exceptions import ConfigurationError
from zope.location import ILocation

from zope.generic.configuration import IConfiguration

from zope.generic.adapter.adapter import ConfigurationAdapterClass



def adapterDirective(_context, provides, for_=None, class_=None, 
                     writePermission=None, readPermission=None, attributes=None,
                     set_attributes=None, key=None, informationProviders=None):
    """Provide a generic locatable and trusted adatpers."""

    # assert for list
    if for_ is None:
        for_ = []

    if class_ and (key or informationProviders):
        raise ConfigurationError('Use class or key/ informationProividers attriubte.')

    # we will provide a generic adapter class
    if class_ is None and IConfiguration.providedBy(provides):
        class_ = ConfigurationAdapterClass(provides, informationProviders)

    if class_ is None and key:
        raise NotImplementedError('Missing feature: You cannot use the key attribute yet.')
        #class_ = AnnotationAdapterClass(provides)

    if class_ is None:
        raise ConfigurationError('No class is given or could be evaluated.')

    # register class and set its permissions
    class_directive = ClassDirective(_context, class_)
    if writePermission:
        # use the provided interface to declare the write permission
        if set_attributes is None:
            class_directive.require(_context, permission=writePermission, set_schema=[provides])

        # use set attributes to declare the write permission
        else:
            class_directive.require(_context, permission=writePermission, set_attributes=set_attributes)

    if readPermission:
        # use the provided interface to declare the read permission
        if attributes is None:
            class_directive.require(_context, permission=readPermission, interface=[provides])

        # use attributes to declare the read permission
        else:
            class_directive.require(_context, permission=writePermission, attributes=attributes)

    # evalute if location is provided by the adapters
    locate = False
    if not ILocation.implementedBy(class_):
        locate = True

    # register adapter
    adapter(_context, factory=[class_], provides=provides, 
            for_=for_, permission=None, name='', trusted=True, 
            locate=locate)
