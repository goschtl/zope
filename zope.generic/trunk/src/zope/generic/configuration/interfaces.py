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

from zope.app.i18n import ZopeMessageFactory as _
from zope.location import ILocation
from zope.component.interfaces import IObjectEvent
from zope.interface import Attribute
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.lifecycleevent.interfaces import IModificationDescription
from zope.schema.interfaces import IField

from zope.generic.face import IFaced
from zope.generic.face import IKeyfaceType



class IConfigurable(Interface):
    """Provides an adapter to IConfigurations."""



class IConfigurationType(IKeyfaceType):
    """Type a key schema that is used for configuration purposes."""



class INestedConfigurationType(IConfigurationType):
    """Type a key schema that contains nested configuraiton."""



class INestedConfiguration(IField):
    """Mark nested configuration."""



class IConfigurationData(IFaced):
    """Marker for configuration data implementations."""



class IReadConfigurations(Interface):
    """Read configuration data or looku for a certain configuration shema."""

    def __conform__(keyface):
        """Invoke configuration data that are stored under the key interface.

        Regularly the interface-key should provide configuration type.
        If no value could be found None is returned.
        """

    def __nonzero__():
        """Test whether there are any configurations at all."""

    def __getitem__(keyface):
        """Return the configuration data stored under key interface.

        Raises a KeyError if the key interface is not found.
        """

    def keys(self):
        """Return stored key interfaces."""



class IUpdateConfigurations(Interface):
    """Update configuration data."""

    def update(keyface, data):
        """Update the configuration data partially if nessecary.

        data - dict providing keys and values corresponding to key interface.
        
        The data object itself will not be saved, only the values that
        differs from the existing configuration data.
        
        A ValueError is raised if an read-only attribute/value should be set.

        A AttributeError is raised if a not declared name should be set.

        A KeyError is raise if there is no corresponding configuration available.
        
        A successfull update is notified by a ObjectConfiguredEvent if
        any value of the configuration data got changed and the surrounding 
        context (parent of the configurations) is providing ILocation.
        """



class IWriteConfigurations(Interface):
    """Set or delete a configuration data."""

    def __setitem__(keyface, configuration_data):
        """Store a certain configuration data under the interface-key.

        The interface key should provide IConfigurationType.

        The configuration data has to provide the declared key interface. 
        
        Configuration data will be invoked by the __conform__ mechanism if
        somebody try to adapt the configurations to corresponding key interface.
        
        A successfull setting is notified by a ObjectConfiguredEvent if
        any value of the configuration data got changed and the surrounding 
        context (parent of the configurations) is providing ILocation.
        """

    def __delitem__(keyface):
        """Removes the configuration data stored under interface-key.

        Raises a KeyError if the key interface is not found.

        A successfull deletion is notified by a ObjectConfiguredEvent if
        any value of the configuration data got changed and the surrounding 
        context (parent of the configurations) is providing ILocation.
        """



class IConfigurations(IReadConfigurations, IUpdateConfigurations, 
                      IWriteConfigurations, IConfigurable, ILocation):
    """United configurations interfaces."""


class IAttributeConfigurable(IConfigurable):
    """Marker indicating that configurations can be stored on an attribute.
    
    This is a marker interface giving permission for an `IConfigurations`
    adapter to store data in an attribute named `__configurations__`.

    """


class IConfigurationModificationDescription(IModificationDescription):
    """Declares the modified configuration by its interface and
    the corresponding data that got modified.

    An empty data dictionary implies that the configuration was deleted."""

    interface = Attribute("The involved configuratoin interface.")
    data = Attribute("A dict of modified configuration data.")



class IObjectConfiguredEvent(IObjectEvent):
    """An object's configurations has been modified.
    
    The corresponding modifications will be attached on the description attribute
    """

    descriptions = Attribute("Sequence of modifiaction descriptions.")

    def items():
        """List affected configuration interfaces and corresponding data from the descriptions."""

    def get(interface, default=None):
        """Return affected configuration data from the description or default."""
