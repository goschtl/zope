##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""utility service

$Id: utility.py,v 1.11 2004/04/12 17:28:55 jim Exp $
"""

from zope.component.exceptions import Invalid, ComponentLookupError
from zope.component.interfaces import IUtilityService, IComponentRegistry
from zope.component.service import GlobalService
from zope.interface.adapter import AdapterRegistry
from zope.interface import implements

class IGlobalUtilityService(IUtilityService, IComponentRegistry):

    def provideUtility(providedInterface, component, name=''):
        """Provide a utility

        A utility is a component that provides an interface.
        """

class GlobalUtilityService(AdapterRegistry, GlobalService):

    implements(IGlobalUtilityService)

    def __init__(self):
        AdapterRegistry.__init__(self)
        self._registrations = {}

    def provideUtility(self, providedInterface, component, name='', info=''):
    
        if not providedInterface.providedBy(component):
            raise Invalid("The registered component doesn't implement "
                          "the promised interface.")

        self.register((), providedInterface, name, component)

        self._registrations[(providedInterface, name)] = UtilityRegistration(
            providedInterface, name, component, info)

    def registrations(self):
        return self._registrations.itervalues()

    def getUtility(self, interface, name=''):
        """See IUtilityService interface"""
        c = self.queryUtility(interface, None, name)
        if c is not None:
            return c
        raise ComponentLookupError(interface)

    def queryUtility(self, interface, default=None, name=''):
        """See IUtilityService interface"""

        byname = self._null.get(interface)
        if byname:
            return byname.get(name, default)
        else:
            return default

    def getUtilitiesFor(self, interface):
        byname = self._null.get(interface)
        if byname:
            for item in byname.iteritems():
                yield item

    def getRegisteredMatching(self, interface=None, name=None):
        # doomed method
        lameresult = []
        for registration in self.registrations():
            if (interface is not None
                and interface is not registration.provided):
                continue
            if (name is not None
                and registration.name.find(name) < 0):
                continue
            lameresult.append((registration.provided, registration.name,
                               registration.value))
        return lameresult
        

class UtilityRegistration(object):

    def __init__(self, provided, name, value, doc):
        self.provided = provided
        self.name = name
        self.value = value
        self.doc = doc

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (
            self.__class__.__name__,
            self.provided.__name__, self.name,
            getattr(self.value, '__name__', self.value), self.doc,
            )

