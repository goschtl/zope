##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Interfaces for objects supporting configuration registration

$Id: ConfigurationInterfaces.py,v 1.6 2002/12/12 11:32:30 mgedmin Exp $
"""

from Interface import Interface
from Interface.Attribute import Attribute
from Zope.Schema import Text, TextLine
from Zope.Schema.IField import ITextLine

Unregistered = u'Unregistered'
Registered = u'Registered'
Active = u'Active'

class IConfigurationStatus(ITextLine):
    """The registration status of a configuration
    """

class ConfigurationStatus(TextLine):
    __implements__ = IConfigurationStatus
    allowed_values = Unregistered, Registered, Active

class IConfigurationSummary(Interface):
    """Configuration summary data
    """

    title = TextLine(title = u"Title",
                 description = u"Descriptive title",
                 required = True)

    status = ConfigurationStatus(title = u"Configuration status")

class IConfiguration(IConfigurationSummary):
    """Configuration object

    A configuration object represents a specific configuration
    decision, such as registering an adapter or defining a permission.

    In addition to the attributes or methods defined here,
    configuration objects will include additional attributes
    identifying how they should be used. For example, a service
    configuration will provide a service type. An adapter
    configuration will specify a used-for interface and a provided
    interface.
    """

    description = Text(title = u"Description",
                       description = u"Detailed description",
                       )

    def activated():
        """Method called when a configuration is made active
        """

    def deactivated():
        """Method called when a configuration is made inactive
        """

class IComponentConfiguration(IConfiguration):
    """Configuration object that configures a component
    """

    componentPath = Attribute("The physical path to the component")

    def getComponent():
        """Return the component named in the configuration.
        """

class INamedComponentConfiguration(IComponentConfiguration):
    """Configuration object that configures a component associated with a name
    """

    name = Attribute("The name of the component")

    label = TextLine(title=u"Label",
                     description=u"Descriptive label of the configuration type"
                                 u" (e.g. Service, Connection)")



class IConfigurationRegistry(Interface):
    """A registry of configurations for a set of parameters

    A service will have a registry containing configuration registries
    for specific parameters. For example, an adapter service will have
    a configuration registry for each given used-for and provided
    interface.
    """

    def register(configuration):
        """Register the given configuration

        Do nothing if the configuration is already registered.
        """

    def unregister(configuration):
        """Unregister the given configuration

        Do nothing if the configuration is not registered.
        """

    def registered(configuration):
        """Is the configuration registered

        Return a boolean indicating whether the configuration has been
        registered.

        """

    def activate(configuration):
        """Make the configuration active.

        The activated method is called on the configuration.

        Raises a ValueError if the given configuration is not registered.
        """

    def deactivate(configuration):
        """Make the configuration inactive.

        Id the configuration is active, the deactivated method is called
        on the configuration.

        Raises a ValueError if the given configuration is not registered.

        The call has no effect if the configuration is registered but
        not active.
        """

    def active():
        """Return the active configuration, if any

        Otherwise, returns None.
        """

    def info():
        """Return a sequence of configuration information

        The sequence items are mapping objects with keys:

        id -- A string that can be used to uniquely identify the
              configuration

        active -- A boolean indicating whether the configuration is
                  active

        configuration -- The configuration object.
        """

    def __nonzero__(self):
        """The registry is true if it is non-empty
        """


class IConfigurable(Interface):

    def queryConfigurationsFor(configuration, default=None):
        """Return an IConfigurationRegistry for the configuration

        Data on the configuration is used to decide which registry to
        return. For example, a service manager will use the
        configuration name attribute to decide which registry
        to return.

        Typically, an object that implements this method will also
        implement a method named queryConfigurations, which takes
        arguments for each of the parameters needed to specify a set
        of configurations.
        """

    def createConfigurationsFor(configuration):
        """Create and return an IConfigurationRegistry for the configuration

        Data on the configuration is used to decide which regsitry to
        create. For example, a service manager will use the
        configuration name attribute to decide which regsitry
        to create.

        Typically, an object that implements this method will also
        implement a method named createConfigurations, which takes
        arguments for each of the parameters needed to specify a set
        of configurations.

        Calling createConfigurationsFor twice for the same configuration
        returns the same registry.
        """


class INameConfigurable(IConfigurable):
    # XXX docstring

    def queryConfigurations(name, default=None):
        """Return an IConfigurationRegistry for the configuration name

        queryConfigurationsFor(cfg, default) is equivalent to
        queryConfigurations(cfg.name, default)
        """

    def createConfigurationsFor(configuration):
        """Create and return an IConfigurationRegistry for the configuration
        name

        createConfigurationsFor(cfg, default) is equivalent to
        createConfigurations(cfg.name, default)
        """

    def listConfigurationNames():
        """Return a list of all registered configuration names
        """

    # XXX It might be useful to abstract out common parts from
    # ServiceManager.getBoundService and ConnectionService.getConnection
    # into a method declared in INameConfigurable.  That would also mean that
    # INameConfigurable relies on configurations implementing
    # INamedComponentConfiguration, while now it is sufficient for a
    # configuration to have a name attribute.
