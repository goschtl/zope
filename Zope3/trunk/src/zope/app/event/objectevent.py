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

$Id: objectevent.py,v 1.7 2003/09/21 17:32:06 jim Exp $
"""

__metaclass__ = type

from zope.app.interfaces.event import IObjectEvent, IObjectCreatedEvent
from zope.app.interfaces.event import IObjectModifiedEvent
from zope.app.interfaces.event import IObjectCopiedEvent
from zope.app.interfaces.event import IObjectAnnotationsModifiedEvent
from zope.app.interfaces.event import IObjectContentModifiedEvent
from zope.app.traversing import getPath
from zope.interface import implements
from zope.app.event import publish

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
