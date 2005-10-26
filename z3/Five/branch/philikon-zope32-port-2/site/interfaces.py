##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
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
"""Five interfaces

$Id: interfaces.py 18584 2005-10-14 17:13:27Z regebro $
"""
from zope.interface import Interface

class IFiveUtilityRegistry(Interface):
    """Extends ILocalUtilityService with a method to register utilities"""
     
    def getUtility(interface, name='', context=None):
        """Get the utility that provides interface

        Returns the nearest utility to the context that implements the
        specified interface.  If one is not found, raises
        ComponentLookupError.
        """

    def queryUtility(interface, name='', default=None, context=None):
        """Look for the utility that provides interface

        Returns the nearest utility to the context that implements
        the specified interface.  If one is not found, returns default.
        """

    def getUtilitiesFor(interface, context=None):
        """Return the utilities that provide an interface

        An iterable of utility name-value pairs is returned.
        """

    def getAllUtilitiesRegisteredFor(interface, context=None):
        """Return all registered utilities for an interface

        This includes overridden utilities.

        An iterable of utility instances is returned.  No names are
        returned.
        """

    def registerUtility(self, interface, utility, name=''):
        """Registers a utility in the local context"""
        # I think you are *really* supposed to:
        # 1. Check if there is a "registrations" object for utilities.
        # 2. If not create one.
        # 3. Get it.
        # 4. Create a registration object for the utility.
        # 5. Register the registration object in the registrations.
        # But that is quite complex, and Jim sais he wants to change that
        # anyway, and in any case the way you would normally do this in Zope3
        # and Five would probably differ anyway, so, here is this new 
        # Five-only, easy to use method!

# BBB 2005/11/01 -- gone in Five 1.5.
IFiveUtilityService = IFiveUtilityRegistry
import zope.deprecation
zope.deprecation.deprecated(
    'IFiveUtilityService', "'IFiveUtilityService' has been renamed to "
    "'IFiveUtilityRegistry' and will disappear in Five 1.5."
    )
