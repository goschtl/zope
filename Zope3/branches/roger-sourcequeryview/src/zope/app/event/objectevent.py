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
"""Object lifetime events.

$Id$
"""
__docformat__ = 'restructuredtext'

from zope.app.event.interfaces import IObjectEvent, IObjectCreatedEvent
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.event.interfaces import IObjectCopiedEvent
from zope.app.event.interfaces import IObjectAnnotationsModifiedEvent
from zope.app.event.interfaces import IObjectContentModifiedEvent
from zope.interface import implements
from zope.event import notify
from zope.component import subscribers

_marker = object()

class ObjectEvent(object):
    """Something has happened to an object"""

    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object

class ObjectCreatedEvent(ObjectEvent):
    """An object has been created"""

    implements(IObjectCreatedEvent)

class ObjectModifiedEvent(ObjectEvent):
    """An object has been modified"""

    implements(IObjectModifiedEvent)

def modified(object):
    notify(ObjectModifiedEvent(object))

class ObjectAnnotationsModifiedEvent(ObjectModifiedEvent):
    """An object's annotations have been modified"""

    implements(IObjectAnnotationsModifiedEvent)

def annotationModified(object):
    notify(ObjectAnnotationModifiedEvent(object))

class ObjectContentModifiedEvent(ObjectModifiedEvent):
    """An object's content has been modified"""

    implements(IObjectContentModifiedEvent)

def contentModified(object):
    notify(ObjectContentModifiedEvent(object))

class ObjectCopiedEvent(ObjectCreatedEvent):
    """An object has been copied"""

    implements(IObjectCopiedEvent)


def objectEventNotify(event):
    """Event subscriber to dispatch ObjectEvents to interested adapters."""
    adapters = subscribers((event.object, event), None)
    for adapter in adapters:
        pass # getting them does the work
