##############################################################################
#
# Copyright (c) 2006 Zope Foundation and Contributors.
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
"""A simple multi-database mount-point implementation

$Id$
"""
__docformat__ = "reStructuredText"
import persistent
import zope.component
import zope.interface
import zope.lifecycleevent
import zope.location
from zope.app.container import contained
from zope.app.publication import traversers
from zope.publisher.interfaces.browser import IBrowserRequest, IBrowserPublisher
from zope.security.proxy import removeSecurityProxy
from zope.traversing import api

from z3c.mountpoint import interfaces, remoteproxy

class MountPoint(persistent.Persistent, contained.Contained):
    """A simple mount point."""
    zope.interface.implements(interfaces.IMountPoint)

    def __init__(self, connectionName=None, objectPath=u'/', objectName=u'object'):
        self.connectionName = connectionName
        self.objectPath = objectPath
        self.objectName = objectName
        self.object = None

    def update(self):
        parent = self.__parent__
        if parent is not None:
            # Get the connection by name
            conn = parent._p_jar.get_connection(self.connectionName)
            obj = conn.root()['Application']
            obj = api.traverse(obj, self.objectPath)
            self.object = obj
        else:
            self.object = None

    @apply
    def __parent__():
        def get(self):
            return self and self.__dict__.get('__parent__', None)
        def set(self, parent):
            self.__dict__['__parent__'] = parent
            self.update()
        return property(get, set)


class MountPointTraverser(traversers.SimpleComponentTraverser):

    zope.component.adapts(interfaces.IMountPoint, IBrowserRequest)
    zope.interface.implementsOnly(IBrowserPublisher)

    def publishTraverse(self, request, name):
        if name == self.context.objectName:
            # Remove the security proxy, because we need a bare object to wrap
            # the location proxy around.
            context = removeSecurityProxy(self.context)
            return remoteproxy.RemoteLocationProxy(
                context.object, context, self.context.objectName)
        return super(MountPointTraverser, self).publishTraverse(
            request, name)


@zope.component.adapter(
    interfaces.IMountPoint, zope.lifecycleevent.IObjectModifiedEvent)
def updateMountedObject(mountPoint, event):
    mountPoint.update()
