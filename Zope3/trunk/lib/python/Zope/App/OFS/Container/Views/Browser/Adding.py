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
"""

$Id: Adding.py,v 1.12 2002/11/30 18:34:34 jim Exp $
"""

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Container.IContainer import IContainerNamesContainer
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.IPublishTraverse import IPublishTraverse
from Zope.ComponentArchitecture \
     import getView, getService, createObject, \
            queryFactory, queryView, getAdapter
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.ContextWrapper import ContextMethod, getbaseobject
from Zope.Proxy.ContextWrapper import ContextWrapper
from Zope.Event import publishEvent
from Zope.Event.ObjectEvent \
     import ObjectCreatedEvent, ObjectModifiedEvent, ObjectAddedEvent
from Zope.App.OFS.Container.IZopeContainer import IZopeContainer
class Adding(BrowserView):

    __implements__ =  IAdding, IPublishTraverse

    menu_id = "add_content"

    ############################################################
    # Implementation methods for interface
    # IAdding.py

    def add(self, content):
        'See Zope.App.OFS.Container.IAdding.IAdding'
        container = self.context
        container = getAdapter(container, IZopeContainer)
        name = container.setObject(self.contentName, content)
        return container[name]

    
    # See Zope.App.OFS.Container.Views.Browser.IAdding.IAdding
    contentName = None # usually set by Adding traverser

    def nextURL(self):
        'See Zope.App.OFS.Container.IAdding.IAdding'
        return (str(getView(self.context, "absolute_url", self.request))
                + '/@@contents.html')

    ######################################
    # from: Zope.ComponentArchitecture.IPresentation.IPresentation

    # See Zope.ComponentArchitecture.IPresentation.IPresentation
    request = None # set in BrowserView.__init__

    ######################################
    # from: Zope.ComponentArchitecture.IContextDependent.IContextDependent

    # See Zope.ComponentArchitecture.IContextDependent.IContextDependent
    context = None # set in BrowserView.__init__

    ######################################
    # from: Zope.Publisher.IPublishTraverse.IPublishTraverse

    def publishTraverse(self, request, name):
        if '=' in name:            
            view_name, content_name = name.split("=", 1)
            self.contentName = content_name

            return getView(self, view_name, request)

        view = queryView(self, name, request)
        if view is not None:
            return view

        factory = queryFactory(self.context, name)
        if factory is None:
            return super(Adding, getbaseobject(self)
                         ).publishTraverse(request, name)

        return factory

    publishTraverse = ContextMethod(publishTraverse)
    
    #
    ############################################################

    index = ViewPageTemplateFile("add.pt")

    def addingInfo(self):
        """Return menu data"""

        menu_service = getService(self.context, "BrowserMenu")
        return menu_service.getMenu(self.menu_id, self, self.request)

    def action(self, type_name, id=''):
        if queryView(self, type_name, self.request) is not None:
            url = "%s=%s" % (type_name, id)
            self.request.response.redirect(url)
            return

        if not id:
            raise ValueError("You must specify an id")

        self.contentName = id
        
        content = createObject(self, type_name)
        publishEvent(self.context, ObjectCreatedEvent(content))
        
        self.add(content)
        self.request.response.redirect(self.nextURL())

    def namesAccepted(self):
        return not IContainerNamesContainer.isImplementedBy(self.context)

