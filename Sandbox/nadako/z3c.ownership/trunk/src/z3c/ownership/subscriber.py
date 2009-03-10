##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Subscriber that sets current principal as object's owner on object creation

$Id$
"""
from zope.component import adapter
from zope.lifecycleevent.interfaces import IObjectCreatedEvent
from zope.security.management import queryInteraction

from z3c.ownership.interfaces import IOwnership, IOwnerAware

def getCurrentPrincipal():
    interaction = queryInteraction()
    if interaction is not None:
        for participation in interaction.participations:
            if participation.principal is not None:
                return participation.principal
    return None

@adapter(IOwnerAware, IObjectCreatedEvent)
def setOwner(object, event):
    principal = getCurrentPrincipal()
    if principal is not None:
        IOwnership(object).owner = principal
