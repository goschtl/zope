##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Role implementation

$Id$
"""
from persistent import Persistent
from zope.interface import implements

from zope.app import zapi
from zope.app.location import Location
from zope.app.securitypolicy.interfaces import IRole

from zope.app.i18n import ZopeMessageIDFactory as _
NULL_ID = _('<role not activated>')

class Role(object):
    implements(IRole)

    def __init__(self, id, title, description=""):
        self.id = id
        self.title = title
        self.description = description


class LocalRole(Persistent, Location):
    implements(IRole)

    def __init__(self, title, description=""):
        self.id = NULL_ID
        self.title = title
        self.description = description

# BBB: Renamed component on 12/05/2004
PersistentRole = LocalRole
from zope.app.component.site import UtilityRegistration
RoleRegistration = UtilityRegistration

def setIdOnActivation(role, event):
    """Set the permission id upon registration activation.

    Let's see how this notifier can be used. First we need to create an event
    using the permission instance and a registration stub:

    >>> class Registration:
    ...     def __init__(self, obj, name):
    ...         self.component = obj
    ...         self.name = name

    >>> role1 = LocalRole('Role 1', 'A first role')
    >>> role1.id
    u'<role not activated>'
    >>> from zope.app.component import registration 
    >>> event = registration.RegistrationActivatedEvent(
    ...     Registration(role1, 'role1'))

    Now we pass the event into this function, and the id of the role should be
    set to 'role1'.

    >>> setIdOnActivation(role1, event)
    >>> role1.id
    'role1'
    """
    role.id = event.object.name


def unsetIdOnDeactivation(role, event):
    """Unset the permission id up registration deactivation.

    Let's see how this notifier can be used. First we need to create an event
    using the permission instance and a registration stub:

    >>> class Registration:
    ...     def __init__(self, obj, name):
    ...         self.component = obj
    ...         self.name = name

    >>> role1 = LocalRole('Role 1', 'A first role')
    >>> role1.id = 'role1'

    >>> from zope.app.component import registration 
    >>> event = registration.RegistrationDeactivatedEvent(
    ...     Registration(role1, 'role1'))

    Now we pass the event into this function, and the id of the role should be
    set to NULL_ID.

    >>> unsetIdOnDeactivation(role1, event)
    >>> role1.id
    u'<role not activated>'
    """
    role.id = NULL_ID



def checkRole(context, role_id):
    names = [name for name, util in zapi.getUtilitiesFor(IRole, context)]
    if not role_id in names:
        raise ValueError("Undefined role id", role_id)
