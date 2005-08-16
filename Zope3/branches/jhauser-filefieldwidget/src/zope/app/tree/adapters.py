##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Object adapters

This module contains adapters necessary to use common objects with
statictree. The most prominent ones are those for ILocation and
IContainer. We also provide adapters for any object, so we don't end
up with ComponentLookupErrors whenever encounter unknown objects.

$Id$
"""
from zope.interface import Interface, implements
from zope.component.exceptions import ComponentLookupError

from zope.app import zapi
from zope.app.location.interfaces import ILocation
from zope.app.container.interfaces import IReadContainer
from zope.app.site.interfaces import ISite

from zope.app.tree.interfaces import IUniqueId, IChildObjects

class StubUniqueId(object):
    implements(IUniqueId)
    __used_for__ = Interface

    def __init__(self, context):
        self.context = context

    def getId(self):
        # this does not work for persistent objects
        return str(id(self.context))

class StubChildObjects(object):
    implements(IChildObjects)
    __used_for__ = Interface

    def __init__(self, context):
        pass

    def hasChildren(self):
        return False

    def getChildObjects(self):
        return ()

class LocationUniqueId(object):
    implements(IUniqueId)
    __used_for__ = ILocation

    def __init__(self, context):
        self.context = context

    def getId(self):
        context = self.context
        if not context.__name__:
            # always try to be unique
            return str(id(context))
        parents = [context.__name__]
        parents += [parent.__name__ for parent in zapi.getParents(context)
                    if parent.__name__]
        return '\\'.join(parents)

class ContainerChildObjects(object):
    implements(IChildObjects)
    __used_for__ = IReadContainer

    def __init__(self, context):
        self.context = context

    def hasChildren(self):
        return bool(len(self.context))

    def getChildObjects(self):
        return self.context.values()

class ContainerSiteChildObjects(ContainerChildObjects):
    """Adapter for read containers which are sites as well. The site
    manager will be treated as just another child object.
    """
    __used_for__ = ISite

    def hasChildren(self):
        if super(ContainerSiteChildObjects, self).hasChildren():
            return True
        try:
            self.context.getSiteManager()
            return True
        except ComponentLookupError:
            return False

    def getChildObjects(self):
        values = super(ContainerSiteChildObjects, self).getChildObjects()
        try:
            return [self.context.getSiteManager()] + list(values)
        except ComponentLookupError:
            return values
