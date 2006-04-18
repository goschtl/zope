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
from zope.schema import Text
from zope.schema import TextLine
from zope.schema import Tuple


###############################################################################
#
# Base key interface related interfaces  
#
###############################################################################

class IKeyfaceProvider(Interface):
    """Assert that a key interface can be looked up.

    The key interface must be provided by adaption to IKeyface."""



class IAttributeKeyface(IKeyfaceProvider):
    """Provide the key interface within the __keyface__ attribute."""

    __keyface__ = Object(
        title=_('Key interface'),
        description=_('Key interface that allows to lookup ' +
                      'key-interface-specific informations such as ' +
                      'configurations providers.'),
        required=True,
        readonly=True,
        schema=IInterface)



class IKeyface(IKeyfaceProvider):
    """Declare a key interface as component-specific key.

    You can use this key to lookup component-specific informations.
    """

    keyface = Object(
        title=_('Key interface'),
        description=_('Key interface of the adapted context.'),
        required=True,
        readonly=True,
        schema=IInterface)



class IKeyfaceDescription(IKeyface):
    """User description about the associated key interface."""

    label = TextLine(title=_('Label'),
        description=_('Label for associated key interface.'),
        required=True
        )  

    hint = Text(title=_('Hint'),
        description=_('Hint explaning the properties of the associated key interface.'),
        required=True
        )


###############################################################################
#
# base configurations related interfaces 
#
###############################################################################

class IConfigurable(Interface):
    """Provides an adapter to IConfigurations."""



class IConfigurationType(IInterface):
    """Mark a schema that is used for configuration."""



class IConfigurationData(IKeyfaceProvider):
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


###############################################################################
#
# base configurations related interfaces 
#
###############################################################################



class IInformationProviderType(IInterface):
    """Mark information interface as information type."""



class IInformationProvider(IKeyfaceDescription):
    """Provide information about a dedicated key interfaces.
    
    A configuration related to the key interface can be stored within the
    provider's configurations.
    
    Dedicated information providers has to extend this interface.
    """



class IInformationProviderInformation(IInformationProvider):
    """Provide information about information providers."""



alsoProvides(IInformationProviderInformation, IInformationProviderType)



###############################################################################
#
# Extended key interface related interfaces 
#
###############################################################################





###############################################################################
#
# Extended configurations related interfaces 
#
###############################################################################

class IAttributeConfigurable(IConfigurable):
    """Marker indicating that configurations can be stored on an attribute.
    
    This is a marker interface giving permission for an `IConfigurations`
    adapter to store data in an attribute named `__configurations__`.

    """


AnnotationKey = 'zope.generic.component.IConfigurations'

class IAnnotationsConfigurable(IConfigurable):
    """Marker indicating that configurations can be stored on annotations.

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

    

class IConfigurationInformation(IInformationProvider):
    """Information about a configuration."""
