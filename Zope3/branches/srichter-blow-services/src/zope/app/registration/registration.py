##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Component registration support for services

$Id: registration.py 28601 2004-12-09 19:20:03Z srichter $
"""

from zope.app.component import registration

RegistrationEvent = registration.RegistrationEvent
RegistrationActivatedEvent = registration.RegistrationActivatedEvent
RegistrationDeactivatedEvent = registration.RegistrationDeactivatedEvent

RegistrationStatusPropery = registration.RegistrationStatusProperty

from zope.app.component.bbb.registration import RegistrationStack
NotifyingRegistrationStack = RegistrationStack

SimpleRegistrationRemoveSubscriber = \
    registration.SimpleRegistrationRemoveSubscriber
SimpleRegistration = registration.SimpleRegistration

ComponentRegistration = registration.ComponentRegistration
ComponentRegistrationAddSubscriber = \
    registration.ComponentRegistrationAddSubscriber
ComponentRegistrationRemoveSubscriber = \
    registration.ComponentRegistrationRemoveSubscriber
RegisterableMoveSubscriber = registration.RegisterableMoveSubscriber

Registered = registration.Registered

RegistrationManager = registration.RegistrationManager

RegisterableContainer = registration.RegisterableContainer
