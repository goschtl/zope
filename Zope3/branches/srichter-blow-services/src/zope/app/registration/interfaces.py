##############################################################################
#
# Copyright (c) 2002-2005 Zope Corporation and Contributors.
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
"""Interfaces for objects supporting registration

$Id: interfaces.py 28654 2004-12-20 21:13:50Z gintautasm $
"""
from zope.interface import Interface, implements
from zope.schema import TextLine
from zope.schema.interfaces import ITextLine
from zope.app.component.interfaces import registration

UnregisteredStatus = registration.InactiveStatus
RegisteredStatus = registration.InactiveStatus
ActiveStatus = registration.ActiveStatus

IRegistrationEvent = registration.IRegistrationEvent
IRegistrationActivatedEvent = registration.IRegistrationActivatedEvent
IRegistrationDeactivatedEvent = registration.IRegistrationDeactivatedEvent

class INoLocalServiceError(Interface):
    """No local service to register with.
    """

class NoLocalServiceError(Exception):
    """No local service to configure

    An attempt was made to register a registration for which there is
    no local service.
    """

    implements(INoLocalServiceError)

IRegistration = registration.IRegistration

class IComponentPath(ITextLine):
    """A component path

    This is just the interface for the ComponentPath field below.  We'll use
    this as the basis for looking up an appropriate widget.
    """

class ComponentPath(TextLine):
    """A component path

    Values of the field are absolute unicode path strings that can be
    traversed to get an object.
    """
    implements(IComponentPath)

IComponentRegistration = registration.IComponentRegistration

from zope.app.component.bbb.interfaces import IRegistrationStack

IRegistry = registration.IRegistry

class IOrderedContainer(Interface):
    """Containers whose items can be reorderd."""

    def moveTop(names):
        """Move the objects corresponding to the given names to the top.
        """

    def moveUp(names):
        """Move the objects corresponding to the given names up.
        """

    def moveBottom(names):
        """Move the objects corresponding to the given names to the bottom.
        """

    def moveDown(names):
        """Move the objects corresponding to the given names down.
        """

IRegistrationManager = registration.IRegistrationManager
IRegisterableContainer = registration.IRegisterableContainer
IRegisterable = registration.IRegisterable

IRegistered = registration.IRegistered

IAttributeRegisterable = IRegisterable

class INoRegistrationManagerError(Interface):
    """No registration manager error
    """

class NoRegistrationManagerError(Exception):
    """No registration manager

    There is no registration manager in a site-management folder, or
    an operation would result in no registration manager in a
    site-management folder.

    """
    implements(INoRegistrationManagerError)

