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

$Id: utility.py,v 1.9 2003/06/06 16:34:53 stevea Exp $
"""

from zope.interface import implements
from persistence.dict import PersistentDict
from persistence import Persistent
from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.configuration import IConfigurable
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.services.utility import IUtilityConfiguration
from zope.app.interfaces.services.utility import ILocalUtilityService
from zope.app.services.configuration import ConfigurationRegistry
from zope.app.services.configuration import ConfigurationStatusProperty
from zope.app.services.configuration import ComponentConfiguration
from zope.component.exceptions import ComponentLookupError
from zope.interface.implementor import ImplementorRegistry
from zope.context import ContextMethod
from zope.app.context import ContextWrapper

class LocalUtilityService(Persistent):

    implements(ILocalUtilityService, IConfigurable, ISimpleService)

    def __init__(self):
        self._utilities = PersistentDict()

    def getUtility(self, interface, name=''):
        utility = self.queryUtility(interface, name=name)
        if utility is None:
            raise ComponentLookupError("utility", interface, name)
        return utility
    getUtility = ContextMethod(getUtility)

    def queryUtility(self, interface, default=None, name=''):
        registry = self.queryConfigurations(name, interface)
        if registry is not None:
            configuration = registry.active()
            if configuration is not None:
                return configuration.getComponent()

        next = getNextService(self, "Utilities")
        return next.queryUtility(interface, default, name)
    queryUtility = ContextMethod(queryUtility)

    def queryConfigurationsFor(self, configuration, default=None):
        return self.queryConfigurations(configuration.name,
                                        configuration.interface,
                                        default)
    queryConfigurationsFor = ContextMethod(queryConfigurationsFor)

    def queryConfigurations(self, name, interface, default=None):
        utilities = self._utilities.get(name)
        if utilities is None:
            return default
        registry = utilities.getRegistered(interface)
        if registry is None:
            return default

        return ContextWrapper(registry, self)
    queryConfigurations = ContextMethod(queryConfigurations)

    def createConfigurationsFor(self, configuration):
        return self.createConfigurations(configuration.name,
                                         configuration.interface)

    createConfigurationsFor = ContextMethod(createConfigurationsFor)

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
    createConfigurations = ContextMethod(createConfigurations)

    def getRegisteredMatching(self):
        L = []
        for name in self._utilities:
            for iface, cr in self._utilities[name].getRegisteredMatching():
                if not cr:
                    continue
                L.append((iface, name, ContextWrapper(cr, self)))
        return L
    getRegisteredMatching = ContextMethod(getRegisteredMatching)


class UtilityConfiguration(ComponentConfiguration):
    """Utility component configuration for persistent components

    This configuration configures persistent components in packages to
    be utilities.

    """

    status = ConfigurationStatusProperty('Utilities')

    implements(IUtilityConfiguration)

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
        # XXX Smells like a dead chicken to me.
        return self.interface
