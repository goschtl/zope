##############################################################################
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
##############################################################################
"""Local utility service implementation.

Besides being functional, this module also serves as an example of
creating a local service; see README.txt.

$Id: utility.py,v 1.2 2003/03/21 21:02:19 jim Exp $
"""

from persistence.dict import PersistentDict
from persistence import Persistent
from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.configuration import IConfigurable
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.services.utility import IUtilityConfiguration
from zope.app.services.configuration import ConfigurationRegistry
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.app.services.configuration import ComponentConfiguration
from zope.app.services.configuration import SimpleConfiguration
from zope.component.exceptions import ComponentLookupError
from zope.component import getAdapter
from zope.component.interfaces import IUtilityService
from zope.interface.implementor import ImplementorRegistry
from zope.proxy.context import ContextAware
from zope.proxy.context import ContextWrapper
from zope.proxy.introspection import removeAllProxies
from zope.app.interfaces.services.configuration import IUseConfiguration
from zope.app.traversing import getPath

class LocalUtilityService(Persistent, ContextAware):

    __implements__ = IUtilityService, IConfigurable, ISimpleService

    def __init__(self):
        self._utilities = PersistentDict()

    def getUtility(self, interface, name=''):
        utility = self.queryUtility(interface, name=name)
        if utility is None:
            raise ComponentLookupError("utility", interface, name)
        return utility

    def queryUtility(self, interface, default=None, name=''):
        registry = self.queryConfigurations(name, interface)
        if registry is not None:
            configuration = registry.active()
            if configuration is not None:
                return configuration.getComponent()

        next = getNextService(self, "Utilities")
        return next.queryUtility(interface, default, name)

    def queryConfigurationsFor(self, configuration, default=None):
        return self.queryConfigurations(configuration.name,
                                        configuration.interface,
                                        default)

    def queryConfigurations(self, name, interface, default=None):
        utilities = self._utilities.get(name)
        if utilities is None:
            return default
        registry = utilities.getRegistered(interface)
        if registry is None:
            return default

        return ContextWrapper(registry, self)

    def createConfigurationsFor(self, configuration):
        return self.createConfigurations(configuration.name,
                                         configuration.interface)

    def createConfigurations(self, name, interface):
        utilities = self._utilities.get(name)
        if utilities is None:
            utilities = ImplementorRegistry(PersistentDict())
            self._utilities[name] = utilities

        registry = utilities.getRegistered(interface)
        if registry is None:
            registry = ConfigurationRegistry()
            utilities.register(interface, registry)

        return ContextWrapper(registry, self)


class UtilityConfiguration(ComponentConfiguration):
    """Utility component configuration for persistent components

    This configuration configures persistent components in packages to
    be utilities.

    """

    status = ConfigurationStatusProperty('Utilities')

    __implements__ = (IUtilityConfiguration,
                      ComponentConfiguration.__implements__)

    def __init__(self, name, interface, component_path, permission=None):
        ComponentConfiguration.__init__(self, component_path, permission)
        self.name = name
        self.interface = interface

    def usageSummary(self):
        # Override IConfiguration.usageSummary()
        s = "%s utility" % self.interface.__name__
        if self.name:
            s += " named %s" % self.name
        return s

    def getInterface(self):
        # ComponentConfiguration calls this when you specify a
        # permission; it needs the interface to create a security
        # proxy for the interface with the given permission.
        return self.interface

    # The following hooks are called only if we implement
    # IAddNotifiable and IDeleteNotifiable.

    def afterAddHook(self, configuration, container):
        """Hook method will call after an object is added to container.

        Defined in IAddNotifiable.
        """
        super(UtilityConfiguration, self).afterAddHook(configuration,
                                                       container)
        utility = configuration.getComponent()
        adapter = getAdapter(utility, IUseConfiguration)
        adapter.addUsage(getPath(configuration))

    def beforeDeleteHook(self, configuration, container):
        """Hook method will call before object is removed from container.

        Defined in IDeleteNotifiable.
        """
        utility = configuration.getComponent()
        adapter = getAdapter(utility, IUseConfiguration)
        adapter.removeUsage(getPath(configuration))
        super(UtilityConfiguration, self).beforeDeleteHook(configuration,
                                                           container)
    
