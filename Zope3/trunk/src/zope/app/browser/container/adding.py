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

$Id: adding.py,v 1.24 2003/12/09 07:35:36 sraju Exp $
"""
__metaclass__ = type

from zope.app import zapi

from zope.app.interfaces.exceptions import UserError

from zope.app.interfaces.container import IAdding
from zope.app.interfaces.container import IContainerNamesContainer
from zope.app.interfaces.container import INameChooser

from zope.app.event.objectevent import ObjectCreatedEvent
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.event import publish
from zope.app.publisher.browser import BrowserView
from zope.publisher.interfaces import IPublishTraverse

from zope.app.i18n import ZopeMessageIDFactory as _
from zope.interface import implements

from zope.app.location import LocationProxy
import zope.security.checker

from zope.proxy import removeAllProxies

from zope.app.container.constraints import checkFactory

class BasicAdding(BrowserView):

    implements(IAdding, IPublishTraverse)

    actionName = 'action.html'

    title = _(u"Add Content")

    addValue = _(u" Add ")

    def add(self, content):
        """See zope.app.interfaces.container.IAdding"""

        container = self.context
        name = self.contentName

        chooser = zapi.getAdapter(container, INameChooser)
        
        if IContainerNamesContainer.isImplementedBy(container):
            # The container pick's it's own names.
            # We need to ask it to pick one.
            name = chooser.chooseName(self.contentName or '', content)
            
        else:
            chooser.checkName(name, container)

        container[name] = content

        return container[name]

    contentName = None # usually set by Adding traverser

    def nextURL(self):
        """See zope.app.interfaces.container.IAdding"""
        return (str(zapi.getView(self.context, "absolute_url", self.request))
                + '/@@contents.html')

    request = None # set in BrowserView.__init__

    context = None # set in BrowserView.__init__


    def renderAddButton(self):
        """To Render Add button with or without Inputbox"""
        container = self.context

        if IContainerNamesContainer.isImplementedBy(container):
            return "<input type='submit' value=' Add '>"
        else:
            return ("<input type='submit' value=' Add '>"
                    "<input type='text' name='add_input_name' value=''>")

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
            return super(BasicAdding, self).publishTraverse(request, name)

        return factory

    def action(self, type_name='', id=''):
        if not type_name:
            raise UserError(_(u"You must select the type of object to add."))

        if type_name.startswith('@@'):
            type_name = type_name[2:]

        if '/' in type_name:
            view_name  = type_name.split('/', 1)[0]
        else:
            view_name = type_name

        if zapi.queryView(self, view_name, self.request) is not None:
            url = "%s/%s=%s" % (
                zapi.getView(self, "absolute_url", self.request),
                type_name, id)
            self.request.response.redirect(url)
            return

        if self.namesAccepted():
            if not id:
                raise UserError(_(u"You must specify an id"))
            self.contentName = id

        factory = zapi.getFactory(self, type_name)
        factory = LocationProxy(factory, self, type_name)
        factory = zope.security.checker.ProxyFactory(factory)
        content = factory()

        # Can't store security proxies.
        # Note that it is important to do this here, rather than
        # in add, otherwise, someone might be able to trick add
        # into unproxying an existing object,
        content = removeAllProxies(content)

        publish(self.context, ObjectCreatedEvent(content))

        self.add(content)
        self.request.response.redirect(self.nextURL())

    def namesAccepted(self):
        return not IContainerNamesContainer.isImplementedBy(self.context)

class Adding(BasicAdding):

    menu_id = None

    index = ViewPageTemplateFile("add.pt")

    def addingInfo(self):
        """Return menu data.

        This is sorted by title.
        """
        container = self.context
        menu_service = zapi.getService(container, "BrowserMenu")
        result = []
        for menu_id in (self.menu_id, 'zope.app.container.add'):
            if not menu_id:
                continue
            for item in menu_service.getMenu(menu_id, self, self.request):
                extra = item.get('extra')
                if extra:
                    factory = extra.get('factory')
                    if factory:
                        factory = zapi.getFactory(container, factory)
                        if not checkFactory(container, None, factory):
                            continue
                result.append(item)
                
        result.sort(lambda a, b: cmp(a['title'], b['title']))
        return result

class ContentAdding(Adding):

    menu_id = "add_content"
