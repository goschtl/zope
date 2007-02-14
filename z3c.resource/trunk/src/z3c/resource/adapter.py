##############################################################################
#
# Copyright (c) 2007 Zope Foundation and Contributors.
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
"""
$Id$
"""

__docformat__ = 'restructuredtext'

import zope.component
import zope.interface
from zope.event import notify
from zope.lifecycleevent import ObjectCreatedEvent
from zope.annotation.interfaces import IAnnotations

from z3c.resource import resource
from z3c.resource import interfaces
from z3c.resource.interfaces import RESOURCE_KEY


@zope.interface.implementer(interfaces.IResource)
@zope.component.adapter(interfaces.IResourceTraversable)
def getResource(context):
    """Adapt an IResourceTraversable object to IResource."""
    annotations = IAnnotations(context)
    try:
        return annotations[RESOURCE_KEY]
    except KeyError:
        res = resource.Resource()
        notify(ObjectCreatedEvent(res))
        annotations[RESOURCE_KEY] = res
        annotations[RESOURCE_KEY].__parent__ = context
        annotations[RESOURCE_KEY].__name__ = '++resource++'
        return annotations[RESOURCE_KEY]
# Help out apidoc
getResource.factory = resource.Resource
