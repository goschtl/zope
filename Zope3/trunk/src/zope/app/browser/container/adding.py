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
"""Adding View

The Adding View is used to add new objects to a container. It is sort of a
factory screen.

$Id: adding.py,v 1.14 2003/08/06 14:41:36 srichter Exp $
"""
__metaclass__ = type

from zope.app import zapi

from zope.app.interfaces.exceptions import UserError

from zope.app.interfaces.container import IAdding
from zope.app.interfaces.container import IContainerNamesContainer
from zope.app.interfaces.container import IZopeContainer

from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.event import publish
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.interface import implements

class BasicAdding(BrowserView):

    implements(IAdding, IPublishTraverse)

    def add(self, content):
        """See zope.app.interfaces.container.IAdding"""
        container = zapi.getAdapter(self.context, IZopeContainer)
        name = container.setObject(self.contentName, content)
        return container[name]

    contentName = None # usually set by Adding traverser

    def nextURL(self):
        """See zope.app.interfaces.container.IAdding"""
        return (str(zapi.getView(self.context, "absolute_url", self.request))
                + '/@@contents.html')

    request = None # set in BrowserView.__init__

    context = None # set in BrowserView.__init__

    def publishTraverse(self, request, name):
        """See zope.app.interfaces.container.IAdding"""
        if '=' in name:
            view_name, content_name = name.split("=", 1)
            self.contentName = content_name

            if view_name.startswith('@@'):
                view_name = view_name[2:]
            return zapi.getView(self, view_name, request)

        if name.startswith('@@'):
            view_name = name[2:]
        else:
            view_name = name

        view = zapi.queryView(self, view_name, request)
        if view is not None:
            return view

        factory = zapi.queryFactory(self.context, name)
        if factory is None:
            return zapi.ContextSuper(Adding, self).publishTraverse(
                request, name)

        return factory

    # See zope.app.interfaces.container.IAdding
    publishTraverse = zapi.ContextMethod(publishTraverse)

    def action(self, type_name='', id=''):
        if not type_name:
            raise UserError(_(u"You must select the type of object to add."))

        if type_name.startswith('@@'):
            type_name = type_name[2:]

        if zapi.queryView(self, type_name, self.request) is not None:
            url = "%s/%s=%s" % (
                zapi.getView(self, "absolute_url", self.request),
                type_name, id)
            self.request.response.redirect(url)
            return

        if not id:
            raise UserError(_(u"You must specify an id"))

        self.contentName = id

        content = zapi.createObject(self, type_name)
        publish(self.context, ObjectCreatedEvent(content))

        self.add(content)
        self.request.response.redirect(self.nextURL())

    action = zapi.ContextMethod(action)
        

    def namesAccepted(self):
        return not IContainerNamesContainer.isImplementedBy(self.context)

class Adding(BasicAdding):

    menu_id = "add_content"

    index = ViewPageTemplateFile("add.pt")

    def addingInfo(wrapped_self):
        """Return menu data.

        This is sorted by title.
        """
        menu_service = zapi.getService(wrapped_self.context, "BrowserMenu")
        result = menu_service.getMenu(wrapped_self.menu_id,
                                      wrapped_self,
                                      wrapped_self.request)
        result.sort(lambda a, b: cmp(a['title'], b['title']))
        return result
    addingInfo = zapi.ContextMethod(addingInfo)
