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

$Id: Adding.py,v 1.1 2002/12/20 10:31:45 srichter Exp $
"""
from Zope.ComponentArchitecture import getAdapter

from Zope.Event import publish
from Zope.Event.ObjectEvent import ObjectAddedEvent

from Zope.Publisher.IPublishTraverse import IPublishTraverse
from Zope.Publisher.VFS.VFSView import VFSView

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Container.IContainer import IContainerNamesContainer
from Zope.App.OFS.Container.IZopeContainer import IZopeContainer


class Adding(VFSView):

    __implements__ =  IAdding, VFSView.__implements__

    ############################################################
    # Implementation methods for interface
    # IAdding.py

    def add(self, content):
        'See Zope.App.OFS.Container.IAdding.IAdding'
        container = self.context
        container = getAdapter(container, IZopeContainer)
        name = container.setObject(self.contentName, content)
        publish(self.context, ObjectAddedEvent(container[name]))
        return container[name]

    def setContentName(self, name):
        self.contentName = name
        
    # See Zope.App.OFS.Container.Views.Browser.IAdding.IAdding
    contentName = None # usually set by setContentName

    ######################################
    # from: Zope.ComponentArchitecture.IPresentation.IPresentation

    # See Zope.ComponentArchitecture.IPresentation.IPresentation
    request = None # set in VFSView.__init__

    ######################################
    # from: Zope.ComponentArchitecture.IContextDependent.IContextDependent

    # See Zope.ComponentArchitecture.IContextDependent.IContextDependent
    context = None # set in VFSView.__init__



