##############################################################################
#
# Copyright (c) 2002 Zope Corporation and Contributors.
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
"""Adding View for IContentContainer

This

$Id: adding.py,v 1.2 2002/12/25 14:13:28 jim Exp $
"""
from zope.component import getAdapter

from zope.event import publish
from zope.app.event.objectevent import ObjectAddedEvent

from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.vfs import VFSView

from zope.app.interfaces.container import IAdding
from zope.app.interfaces.container import IContainerNamesContainer
from zope.app.interfaces.container import IZopeContainer


class Adding(VFSView):

    __implements__ =  IAdding, VFSView.__implements__

    ############################################################
    # Implementation methods for interface
    # IAdding.py

    def add(self, content):
        'See IAdding'
        container = self.context
        container = getAdapter(container, IZopeContainer)
        name = container.setObject(self.contentName, content)
        publish(self.context, ObjectAddedEvent(container[name]))
        return container[name]

    def setContentName(self, name):
        self.contentName = name

    # See IAdding
    contentName = None # usually set by setContentName

    # See IPresentation
    request = None # set in VFSView.__init__

    # See IContextDependent
    context = None # set in VFSView.__init__
