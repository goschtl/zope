##############################################################################
#
# Copyright (c) 2002, 2003 Zope Corporation and Contributors.
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
"""Event-related interfaces

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.interface import Interface, Attribute

class IObjectEvent(Interface):
    """Something has happened to an object.

    The object that generated this event is not necessarily the object
    refered to by location.
    """

    object = Attribute("The subject of the event.")

class IObjectCreatedEvent(IObjectEvent):
    """An object has been created.

    The location will usually be ``None`` for this event."""

class IObjectCopiedEvent(IObjectCreatedEvent):
    """An object has been copied"""

class IObjectModifiedEvent(IObjectEvent):
    """An object has been modified"""

class IObjectAnnotationsModifiedEvent(IObjectModifiedEvent):
    """An object's annotations have been modified"""

class IObjectContentModifiedEvent(IObjectModifiedEvent):
    """An object's content has been modified"""
