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

$Id: utility.py,v 1.14 2003/08/07 15:29:48 sidnei Exp $
"""

from zope.interface import implements
from persistence.dict import PersistentDict
from persistence import Persistent
from zope.app.component.nextservice import getNextService
from zope.app.interfaces.services.registration import IRegistry
from zope.app.interfaces.services.service import ISimpleService
from zope.app.interfaces.services.utility import IUtilityRegistration
from zope.app.interfaces.services.utility import ILocalUtilityService
from zope.app.services.registration import RegistrationStack
from zope.app.services.registration import ComponentRegistration
from zope.component.exceptions import ComponentLookupError
from zope.interface.implementor import ImplementorRegistry
from zope.context import ContextMethod
from zope.app.context import ContextWrapper

class LocalUtilityService(Persistent):

    implements(ILocalUtilityService, IRegistry, ISimpleService)

    def __init__(self):
        self._utilities = PersistentDict()

    def getUtility(self, interface, name=''):
        utility = self.queryUtility(interface, name=name)
        if utility is None:
            raise ComponentLookupError("utility", interface, name)
        return utility
    getUtility = ContextMethod(getUtility)

    def queryUtility(self, interface, default=None, name=''):
        stack = self.queryRegistrations(name, interface)
        if stack is not None:
            registration = stack.active()
            if registration is not None:
                return registration.getComponent()

        next = getNextService(self, "Utilities")
        return next.queryUtility(interface, default, name)
    queryUtility = ContextMethod(queryUtility)

    def queryRegistrationsFor(self, registration, default=None):
        return self.queryRegistrations(registration.name,
                                        registration.interface,
                                        default)
    queryRegistrationsFor = ContextMethod(queryRegistrationsFor)

    def queryRegistrations(self, name, interface, default=None):
        utilities = self._utilities.get(name)
        if utilities is None:
            return default
        stack = utilities.getRegistered(interface)
        if stack is None:
            return default

        return ContextWrapper(stack, self)
    queryRegistrations = ContextMethod(queryRegistrations)

    def createRegistrationsFor(self, registration):
        return self.createRegistrations(registration.name,
                                         registration.interface)

    createRegistrationsFor = ContextMethod(createRegistrationsFor)

    def createRegistrations(self, name, interface):
        utilities = self._utilities.get(name)
        if utilities is None:
            utilities = ImplementorRegistry(PersistentDict())
            self._utilities[name] = utilities

        stack = utilities.getRegistered(interface)
        if stack is None:
            stack = RegistrationStack()
            utilities.register(interface, stack)

        return ContextWrapper(stack, self)
    createRegistrations = ContextMethod(createRegistrations)

    def getRegisteredMatching(self, interface=None, name=None):
        L = []
        for reg_name in self._utilities:
            for iface, cr in self._utilities[reg_name].getRegisteredMatching():
                if not cr:
                    continue
                if interface and not iface is interface:
                    continue
                if name is not None and reg_name.find(name) < 0:
                    continue
                L.append((iface, reg_name, ContextWrapper(cr, self)))
        return L
    getRegisteredMatching = ContextMethod(getRegisteredMatching)

    def getUtilitiesFor(self, interface=None):
        utilities = {}
        for name in self._utilities:
            for iface, cr in self._utilities[name].getRegisteredMatching():
                if not cr:
                    continue
                if interface and not iface is interface:
                    continue
                cr = ContextWrapper(cr, self)
                utility = cr.active().getComponent()
                utilities[(name, utility)] = None

        next = getNextService(self, "Utilities")

        for utility in next.getUtilitiesFor(interface):
            if not utilities.has_key(utility):
                utilities[utility] = None
        return utilities.keys()
    getUtilitiesFor = ContextMethod(getUtilitiesFor)

class UtilityRegistration(ComponentRegistration):
    """Utility component registration for persistent components

    This registration configures persistent components in packages to
    be utilities.

    """

    serviceType = 'Utilities'

    implements(IUtilityRegistration)

    def __init__(self, name, interface, component_path, permission=None):
        ComponentRegistration.__init__(self, component_path, permission)
        self.name = name
        self.interface = interface

    def usageSummary(self):
        # Override IRegistration.usageSummary()
        s = "%s utility" % self.interface.__name__
        if self.name:
            s += " named %s" % self.name
        return s

    def getInterface(self):
        # ComponentRegistration calls this when you specify a
        # permission; it needs the interface to create a security
        # proxy for the interface with the given permission.
        # XXX Smells like a dead chicken to me.
        return self.interface


# XXX Pickle backward compatability
UtilityConfiguration = UtilityRegistration
