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

$Id: configuration.py,v 1.8 2003/03/21 21:04:12 jim Exp $
"""

from zope.app.interfaces.annotation import IAnnotatable
from zope.app.interfaces.annotation import IAttributeAnnotatable
from zope.app.interfaces.container  import IContainerNamesContainer
from zope.app.security.permission import PermissionField
from zope.interface import Interface, Attribute
from zope.schema import Text, TextLine
from zope.schema.interfaces import ITextLine

Unregistered = u'Unregistered'
Registered = u'Registered'
Active = u'Active'

class IConfigurationStatus(ITextLine):
    """The registration status of a configuration
    """

class ConfigurationStatus(TextLine):
    __implements__ = IConfigurationStatus
    allowed_values = Unregistered, Registered, Active

class IConfiguration(Interface):
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

    status = ConfigurationStatus(title = u"Configuration status")

    def activated():
        """Method called when a configuration is made active
        """

    def deactivated():
        """Method called when a configuration is made inactive
        """

    def usageSummary():
        """Text for line 1 of configuration manager summary"""

    def implementationSummary():
        """Text for line 2 of configuration manager summary"""


class INamedConfiguration(IConfiguration):
    """Configuration object that is registered only by name.
    """

    name = TextLine(title=u"Name",
                    description=u"The name that is registered",
                    readonly=True,
                    # Don't allow empty or missing name:
                    required=True,
                    min_length=1,
                    )

    # The label is generally set as a class attribute on the
    # configuration class.
    label = Attribute("Descriptive label of the configuration type "
                      "(for example, Service, Connection)")


class IComponentPath(ITextLine):
    """A component path
    """
    # This is juse the interface for the ComponentPath field below.
    # We'll use this as the basis for looking up an appriate widget.

class ComponentPath(TextLine):
    """A component path

    Values of the field are absolute unicode path strings that can be
    traversed to get an object.
    """
    __implements__ = IComponentPath


class IComponentConfiguration(IConfiguration):
    """Configuration object that uses a component path and a permission."""

    componentPath = ComponentPath(
        title=u"Component path",
        description=u"The physical path to the component",
        required=True)

    permission = PermissionField(
        title=u"The permission needed to use the component.",
        required=False,
        )

    def getComponent():
        """Return the component named in the configuration.
        """


class INamedComponentConfiguration(INamedConfiguration,
                                   IComponentConfiguration):
    """Components registered by name, using componemt path and permission."""


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
    """A component that can be configured using a configuration manager."""

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

        The registry must be returned wrapped in the context of the
        configurable.

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

        The registry must be returned wrapped in the context of the
        configurable.

        """


class INameConfigurable(IConfigurable):
    """An IConfigurable, where a name is used to decide which registry to
    return for methods in IConfigurable.

    All configurations that pass through queryConfigurationsFor and
    createConfigurationsFor are expected to implement INamedConfiguration.
    """

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

class INameComponentConfigurable(INameConfigurable):
    """An INameConfigurable where the configurations refer to components.

    All configurations that pass through queryConfigurationsFor and
    createConfigurationsFor are expected to implement
    INamedComponentConfiguration.
    """
    def queryActiveComponent(name, default=None):
        """Finds the configuration registry for a given name, checks if it has
        an active configuration, and if so, returns its component.  Otherwise
        returns default.
        """

class IUseConfigurable(IAnnotatable):
    """A marker interface."""

class IUseConfiguration(IUseConfigurable):
    """An object that can keep track of its configured uses.

    The object need not implement this functionality itself, but must at
    least support doing so via an adapter.
    """

    def addUsage(location):
        """Add a usage by location.

        The location is the physical path to the configuration object that
        configures the usage.
        """
    def removeUsage(location):
        """Remove a usage by location.

        The location is the physical path to the configuration object that
        configures the usage.
        """
    def usages():
        """Return a sequence of locations.

        A location is a physical path to a configuration object that
        configures a usage.
        """

class IAttributeUseConfigurable(IAttributeAnnotatable, IUseConfigurable):
    """A marker interface."""


class IOrderedContainer(Interface):
    """Containers whose items can be reorderd.

    XXX This is likely to go.
    """

    def moveTop(names):
        """Move the objects corresponding to the given names to the top
        """

    def moveUp(names):
        """Move the objects corresponding to the given names up
        """

    def moveBottom(names):
        """Move the objects corresponding to the given names to the bottom
        """

    def moveDown(names):
        """Move the objects corresponding to the given names down
        """

class IConfigurationManager(IContainerNamesContainer, IOrderedContainer):
    """Manage Configurations
    """
