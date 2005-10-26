##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
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
"""Local utility registration

$Id$
"""
from zope.interface import implements
from zope.component.exceptions import ComponentLookupError

from OFS.Folder import Folder
from Products.Five.site.interfaces import IFiveUtilityService

class SimpleLocalUtilityService:
    implements(IFiveUtilityService)

    def __init__(self, context):
        self.context = context

    def getUtility(self, interface, name=''):
        """See IUtilityService interface
        """
        c = self.queryUtility(interface, name)
        if c is not None:
            return c
        raise ComponentLookupError(interface, name)

    def queryUtility(self, interface, name='', default=None):
        """See IUtilityService interface
        """
        if name == '':
            # Singletons. Only one per interface allowed, so, let's call it
            # by the interface.
            name = interface.getName()
        else:
            name = interface.getName() + '-' + name
        utilities = getattr(self.context, 'utilities', None)
        if utilities is None:
            return default
        utility = utilities._getOb(name, None)
        if utility is None:
            return default
        if not interface.providedBy(utility):
            return default
        return utility

    def getUtilitiesFor(self, interface):
        utilities = getattr(self.context, 'utilities', None)
        if utilities is None:
            raise StopIteration
        for utility in utilities.objectValues():
            if interface.providedBy(utility):
                yield (utility.getId(), utility)

    def getAllUtilitiesRegisteredFor(self, interface):
        # This also supposedly returns "overridden" utilities, but we don't
        # keep them around. It also does not return the name-value pair that
        # getUtilitiesFor returns.
        utilities = getattr(self.context, 'utilities', None)
        if utilities is None:
            raise StopIteration
        for utility in utilities.objectValues():
            if interface.providedBy(utility):
                yield utility

    def registerUtility(self, interface, utility, name=''):
        # I think you are *really* supposed to:
        # 1. Check if there is a "registrations" object for utilities.
        # 2. If not create one.
        # 3. Get it.
        # 4. Create a registration object for the utility.
        # 5. Rgister the registration object in the registrations.
        # But that is quite complex, and Jim sais he wants to change that
        # anyway, and in any case the way you would normally do this in Zope3
        # and Five would probably differ anyway, so, here is this new
        # Five-only, easy to use method!

        utilities = getattr(self.context, 'utilities', None)
        if utilities is None:
            self.context._setObject('utilities', Folder('utilities'))
            utilities = self.context.utilities

        if name == '':
            # Singletons. Only one per interface allowed, so, let's call it
            # by the interface.
            name = interface.getName()
        else:
            name = interface.getName() + '-' + name

        utilities._setObject(name, utility)
