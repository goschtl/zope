############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
"""Component and Component Architecture Interfaces
"""
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import implements

# BBB 2011-09-09, import interfaces from zope.interface 
from zope.interface.interfaces import ComponentLookupError
from zope.interface.interfaces import Invalid
from zope.interface.interfaces import Misused
from zope.interface.interfaces import IObjectEvent
from zope.interface.interfaces import ObjectEvent
from zope.interface.interfaces import IComponentArchitecture
from zope.interface.interfaces import IComponentLookup
from zope.interface.interfaces import IComponentRegistrationConvenience
from zope.interface.interfaces import IRegistry
from zope.interface.interfaces import IFactory
from zope.interface.interfaces import IRegistration
from zope.interface.interfaces import IUtilityRegistration
from zope.interface.interfaces import _IBaseAdapterRegistration
from zope.interface.interfaces import IAdapterRegistration
from zope.interface.interfaces import ISubscriptionAdapterRegistration
from zope.interface.interfaces import IHandlerRegistration
from zope.interface.interfaces import IRegistrationEvent
from zope.interface.interfaces import RegistrationEvent
from zope.interface.interfaces import IRegistered
from zope.interface.interfaces import Registered
from zope.interface.interfaces import IUnregistered
from zope.interface.interfaces import Unregistered
from zope.interface.interfaces import IComponentRegistry
from zope.interface.interfaces import IComponents

class IPossibleSite(Interface):
    """An object that could be a site.
    """

    def setSiteManager(sitemanager):
        """Sets the site manager for this object.
        """

    def getSiteManager():
        """Returns the site manager contained in this object.

        If there isn't a site manager, raise a component lookup.
        """


class ISite(IPossibleSite):
    """Marker interface to indicate that we have a site"""

