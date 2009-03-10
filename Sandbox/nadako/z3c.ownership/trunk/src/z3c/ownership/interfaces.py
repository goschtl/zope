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
"""Ownership-related interfaces

$Id$
"""
from zope.component.interfaces import IObjectEvent, ObjectEvent
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implements
from zope.schema import Object
from zope.security.interfaces import IPrincipal

_ = MessageFactory('z3c.ownership')

OWNER_ROLE = 'z3c.ownership.Owner'

class IOwnerAware(Interface):
    """Marker interface for objects that supports ownership"""

class IOwnership(Interface):
    """Objects that support ownership provide this interface"""

    owner = Object(
        title=_(u'Owner'),
        description=_(u'Principal that owns this object'),
        schema=IPrincipal,
        required=False,
        )    

class IOwnerChangedEvent(IObjectEvent):
    """Event that is fired when owner changes"""
    
    oldOwner = Object(
        title=_(u'Old owner'),
        schema=IPrincipal,
        required=False
        )

    newOwner = Object(
        title=_(u'New owner'),
        schema=IPrincipal,
        required=False
        )

class OwnerChangedEvent(ObjectEvent):
    """Event that is fired when owner changes"""
    
    implements(IOwnerChangedEvent)
    
    def __init__(self, object, newOwner, oldOwner):
        self.object = object
        self.newOwner = newOwner
        self.oldOwner = oldOwner
