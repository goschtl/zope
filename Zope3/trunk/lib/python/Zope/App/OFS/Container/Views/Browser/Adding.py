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

$Id: Adding.py,v 1.16 2002/12/17 19:13:32 stevea Exp $
"""

from Zope.App.OFS.Container.IAdding import IAdding
from Zope.App.OFS.Container.IContainer import IContainerNamesContainer
from Zope.Publisher.Browser.BrowserView import BrowserView
from Zope.Publisher.IPublishTraverse import IPublishTraverse
from Zope.ComponentArchitecture \
     import getView, getService, createObject, \
            queryFactory, queryView, getAdapter
from Zope.App.PageTemplate import ViewPageTemplateFile
from Zope.ContextWrapper import ContextMethod 
from Zope.Event import publish
from Zope.Event.ObjectEvent import ObjectCreatedEvent
from Zope.App.OFS.Container.IZopeContainer import IZopeContainer
from Zope.ContextWrapper import ContextSuper

class Adding(BrowserView):

    __implements__ =  IAdding, IPublishTraverse

    menu_id = "add_content"

    ############################################################
    # Implementation methods for interface
    # IAdding.py

    def add(self, content):
        'See Zope.App.OFS.Container.IAdding.IAdding'
        container = getAdapter(self.context, IZopeContainer)
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
            return ContextSuper(Adding, self).publishTraverse(request, name)

        return factory
    publishTraverse = ContextMethod(publishTraverse)
    
    #
    ############################################################

    index = ViewPageTemplateFile("add.pt")

    def addingInfo(wrapped_self):
        """Return menu data"""
        menu_service = getService(wrapped_self.context, "BrowserMenu")
        return menu_service.getMenu(wrapped_self.menu_id,
                                    wrapped_self,
                                    wrapped_self.request)
    addingInfo = ContextMethod(addingInfo)

    def action(self, type_name, id=''):
        if queryView(self, type_name, self.request) is not None:
            url = "%s=%s" % (type_name, id)
            self.request.response.redirect(url)
            return

        if not id:
            raise ValueError("You must specify an id")

        self.contentName = id
        
        content = createObject(self, type_name)
        publish(self.context, ObjectCreatedEvent(content))
        
        self.add(content)
        self.request.response.redirect(self.nextURL())

    def namesAccepted(self):
        return not IContainerNamesContainer.isImplementedBy(self.context)

