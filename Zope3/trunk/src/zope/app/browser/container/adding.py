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

$Id: adding.py,v 1.11 2003/06/05 12:41:53 stevea Exp $
"""
__metaclass__ = type

from zope.app.interfaces.exceptions import UserError

from zope.app.interfaces.container import IAdding
from zope.app.interfaces.container import IContainerNamesContainer
from zope.app.interfaces.container import IZopeContainer

from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.component import \
     getView, getService, createObject, queryFactory, queryView, getAdapter
from zope.app.event import publish
from zope.context import ContextSuper, ContextMethod
from zope.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.interface import implements

class Adding(BrowserView):

    implements(IAdding, IPublishTraverse)

    menu_id = "add_content"

    ############################################################
    # Implementation methods for interface
    # IAdding.py

    def add(self, content):
        container = getAdapter(self.context, IZopeContainer)
        name = container.setObject(self.contentName, content)
        return container[name]

    contentName = None # usually set by Adding traverser

    def nextURL(self):
        return (str(getView(self.context, "absolute_url", self.request))
                + '/@@contents.html')

    request = None # set in BrowserView.__init__

    context = None # set in BrowserView.__init__

    def publishTraverse(self, request, name):
        if '=' in name:
            view_name, content_name = name.split("=", 1)
            self.contentName = content_name

            if view_name.startswith('@@'):
                view_name = view_name[2:]
            return getView(self, view_name, request)

        if name.startswith('@@'):
            view_name = name[2:]
        else:
            view_name = name

        view = queryView(self, view_name, request)
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
        """Return menu data.

        This is sorted by title.
        """
        menu_service = getService(wrapped_self.context, "BrowserMenu")
        result = menu_service.getMenu(wrapped_self.menu_id,
                                      wrapped_self,
                                      wrapped_self.request)
        result.sort(lambda a, b: cmp(a['title'], b['title']))
        return result
    addingInfo = ContextMethod(addingInfo)

    def action(self, type_name='', id=''):
        if not type_name:
            raise UserError(_(u"You must select the type of object to add."))

        if type_name.startswith('@@'):
            type_name = type_name[2:]

        if queryView(self, type_name, self.request) is not None:
            url = "%s=%s" % (type_name, id)
            self.request.response.redirect(url)
            return

        if not id:
            raise ValueError(_(u"You must specify an id"))

        self.contentName = id

        content = createObject(self, type_name)
        publish(self.context, ObjectCreatedEvent(content))

        self.add(content)
        self.request.response.redirect(self.nextURL())

    def namesAccepted(self):
        return not IContainerNamesContainer.isImplementedBy(self.context)
