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

from BTrees.OOBTree import OOBTree
import transaction
from UserDict import DictMixin

from zope.app.location import Location
from zope.app.location.interfaces import ILocation
from zope.component import adapts
from zope.event import notify
from zope.interface import implements

from zope.generic.component.api import toDottedName
from zope.generic.component.api import toComponent

from zope.generic.configuration import IAttributeConfigurable
from zope.generic.configuration import IConfigurationType
from zope.generic.configuration import IConfigurations
from zope.generic.configuration.event import Configuration
from zope.generic.configuration.event import ObjectConfigurationsModifiedEvent
from zope.generic.configuration.helper import configuratonToDict




class AttributeConfigurations(DictMixin, Location):
    """Store configurations on an object within the __configurations__ attribute.

    """

    implements(IConfigurations)

    adapts(IAttributeConfigurable)

    def __init__(self, context):
        self.context = context

    def __nonzero__(self):
        return bool(getattr(self.context, '__configurations__', 0))

    def __conform__(self, interface):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            return None

        else:
            return configurations.get(toDottedName(interface), None)

    def __getitem__(self, interface):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            raise KeyError(interface)

        return configurations[toDottedName(interface)]

    def keys(self):
        configurations = getattr(self.context, '__configurations__', None)
        if configurations is None:
            return []

        return [toComponent(iface) for iface in configurations.keys()]

    def update(self, interface, data):
        current_config = self[interface]

        updated_data = {}
        errors = []
        
        savepoint = transaction.savepoint()
        try:
            for name, value in data.items():
                # raise attribute error
                field = interface[name]
                if field.readonly:
                    raise ValueError(name, 'Data is readonly.')
                else:
                    if value != getattr(current_config, name, field.missing_value):
                        setattr(current_config, name, value)
                        updated_data[name] = value

            # notify update
            parent = self.__parent__
            if updated_data and ILocation.providedBy(parent) and parent.__parent__ is not None:
                notify(ObjectConfigurationsModifiedEvent(parent, 
                    Configuration(interface, updated_data)))

        except:
            savepoint.rollback()
            raise

    def __setitem__(self, interface, value):
        # preconditions
        if not IConfigurationType.providedBy(interface):
            raise KeyError('Interface key %s does not provide %s.' % 
                (interface.__name__, IConfigurationType.__name__))

        if not interface.providedBy(value):
            raise ValueError('Value does not provide %s.' % interface.__name__)

        # essentials
        try:
            configurations = self.context.__configurations__
        except AttributeError:
            configurations = self.context.__configurations__ = OOBTree()

        data = configuratonToDict(interface, value, all=True)
        configurations[toDottedName(interface)] = value
        # notify setting
        parent = self.__parent__
        if ILocation.providedBy(parent) and parent.__parent__ is not None:
            notify(ObjectConfigurationsModifiedEvent(parent, 
                Configuration(interface, data)))

    def __delitem__(self, interface):
        try:
            configurations = self.context.__configurations__
        except AttributeError:
            raise KeyError(interface)

        del configurations[toDottedName(interface)]
        # notify deletion
        # notify setting
        parent = self.__parent__
        if ILocation.providedBy(parent) and parent.__parent__ is not None:
            notify(ObjectConfigurationsModifiedEvent(parent, 
                Configuration(interface, {})))
