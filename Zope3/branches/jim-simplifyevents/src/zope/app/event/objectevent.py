##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Object lifetime events.

$Id$
"""

__metaclass__ = type

from zope.app.event.interfaces import IObjectEvent, IObjectCreatedEvent
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.event.interfaces import IObjectCopiedEvent
from zope.app.event.interfaces import IObjectAnnotationsModifiedEvent
from zope.app.event.interfaces import IObjectContentModifiedEvent
from zope.app.event.interfaces import ISubscriber
from zope.interface import implements
from zope.app.event import publish
from zope.component import subscribers

_marker = object()

class ObjectEvent:
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
    publish(object, ObjectModifiedEvent(object))

class ObjectAnnotationsModifiedEvent(ObjectModifiedEvent):
    """An object's annotations have been modified"""

    implements(IObjectAnnotationsModifiedEvent)

def annotationModified(object):
    publish(object, ObjectAnnotationModifiedEvent(object))

class ObjectContentModifiedEvent(ObjectModifiedEvent):
    """An object's content has been modified"""

    implements(IObjectContentModifiedEvent)

def contentModified(object):
    publish(object, ObjectContentModifiedEvent(object))

class ObjectCopiedEvent(ObjectCreatedEvent):
    """An object has been copied"""

    implements(IObjectCopiedEvent)


class ObjectEventNotifier:
    """Event subscriber to dispatch ObjectEvents to interested adapters."""
    implements(ISubscriber)

    def notify(self, event):
        assert IObjectEvent.providedBy(event)
        adapters = subscribers((event.object, event), ISubscriber)
        for adapter in adapters:
            adapter.notify(event)

objectEventNotifierInstance = ObjectEventNotifier()

def objectEventCallbackHelper(callback):
    """Build a factory implementing ISubscriber that just calls a callback

    callback will be called with an ObjectEvent instance. Example usage:

    factory = objectEventCallbackHelper(events.append)
    getService(None, Adapters).subscribe(
        [MyObjectType, IObjectRemovedEvent], ISubscriber, factory
    )
    """
    class _CallbackHelper:
        implements(ISubscriber)           
        def __init__(self, object, event):
            self.object = object
            self.event = event

        def notify(self, event):
            callback(event)

    return _CallbackHelper


