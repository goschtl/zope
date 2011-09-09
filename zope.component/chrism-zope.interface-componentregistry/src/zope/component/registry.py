##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""Basic components support
"""
# BBB, import component-related from zope.interface
from zope.interface.component import Components
from zope.interface.component import _getUtilityProvided
from zope.interface.component import _getAdapterProvided
from zope.interface.component import _getAdapterRequired
from zope.interface.component import UtilityRegistration
from zope.interface.component import AdapterRegistration
from zope.interface.component import SubscriptionRegistration
from zope.interface.component import HandlerRegistration

from zope.component._api import handle
from zope.component._declaration import adapter

from zope.component.interfaces import IAdapterRegistration
from zope.component.interfaces import IHandlerRegistration
from zope.component.interfaces import IRegistrationEvent
from zope.component.interfaces import ISubscriptionAdapterRegistration
from zope.component.interfaces import IUtilityRegistration

@adapter(IUtilityRegistration, IRegistrationEvent)
def dispatchUtilityRegistrationEvent(registration, event):
    handle(registration.component, event)

@adapter(IAdapterRegistration, IRegistrationEvent)
def dispatchAdapterRegistrationEvent(registration, event):
    handle(registration.factory, event)

@adapter(ISubscriptionAdapterRegistration, IRegistrationEvent)
def dispatchSubscriptionAdapterRegistrationEvent(registration, event):
    handle(registration.factory, event)

@adapter(IHandlerRegistration, IRegistrationEvent)
def dispatchHandlerRegistrationEvent(registration, event):
    handle(registration.handler, event)
