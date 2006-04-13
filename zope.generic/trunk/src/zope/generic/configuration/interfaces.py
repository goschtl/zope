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

from zope.app.event.interfaces import IModificationDescription
from zope.app.event.interfaces import IObjectEvent
from zope.app.i18n import ZopeMessageFactory as _
from zope.app.location import ILocation
from zope.interface import Interface
from zope.interface import alsoProvides
from zope.interface import Attribute
from zope.interface.interfaces import IInterface
from zope.schema import Bool
from zope.schema import Dict
from zope.schema import Object
from zope.schema import Tuple

from zope.generic.component import IKeyInterface
from zope.generic.information import IInformation




AnnotationKey = 'zope.generic.configuration.IConfigurations'



class IConfigurable(Interface):
    """Marker interface for objects that support storing configuraitons."""



class IAttributeConfigurable(IConfigurable):
    """Marker indicating that configurations can be stored on an attribute.
    
    This is a marker interface giving permission for an `IConfigurations`
    adapter to store data in an attribute named `__configurations__`.

    """



class IAnnotationsConfigurable(IConfigurable):
    """Marker indicating that configurations can be stored on annotations.

    """



class IConfigurationType(IInterface):
    """Mark a configuration data schema.
    
    Typed schemas might be rendered to xml to provide a configuration view of an
    object.
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



class IReadConfigurations(Interface):
    """Read configurations."""

    def __conform__(interface):
        """Invoke values that are stored under the interface-key.

        Regularly the interface-key should provide configuration type.
        If no value could be found None is returned.
        """

    def __nonzero__():
        """Test whether there are any configurations."""

    def __getitem__(interface):
        """Return the configuration stored under interface-key.

        Raises a KeyError if the key is not found.
        """

    def keys(self):
        """Return stored configuraitons keys."""



class IUpdateConfigurations(Interface):
    """Update configurations."""

    def update(interface, data):
        """Update configuration partially if nessecary.

        data - dict providing values corresponding to the attribute names of the 
            interface.
        
        The data object itself will not be saved, only the values that
        differs from the existing configuration data within the configurations.
        
        A ValueError is raised if an read-only attribute/value should be set.
        A AttributeError is raised if a not declared name should be set.
        A KeyError is raise if there is no corresponding configuration avaiable.
        
        A successfull update is notified by a ObjectConfigurationModifiedEvent if
        any value of the configuration got changed and the parent providing 
        ILocation.
        """



class IWriteConfigurations(Interface):
    """Set or delete a configuration."""

    def __setitem__(interface, value):
        """Store a certain configuration data under the interface-key.

        The interface should provide IConfigurationType.

        The value has to provide the declared interface key and this value will
        be invoked by the __conform__ mechanism if somebody try to adapt the 
        configuration data to this interface.
        
        A successfull setting is notified by a ObjectConfigurationModifiedEvent
        if the parent providing ILocation.
        """

    def __delitem__(interface):
        """Removes the configuration stored under interface-key.

        Raises a KeyError if the key is not found.

        A successfull deletion is notified by a ObjectConfigurationModifiedEvent
        if the parent providing ILocation.
        """



class IConfigurations(IReadConfigurations, IUpdateConfigurations, 
                      IWriteConfigurations, IConfigurable, ILocation):
    """United configurations interfaces."""

    

class IConfigurationInformation(IInformation):
    """Information about a configuration."""

