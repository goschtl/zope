##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Tools View

$Id: tools.py,v 1.2 2004/03/21 17:09:41 srichter Exp $
"""
from zope.interface import implements, Attribute
from zope.interface.interfaces import IInterface
from zope.component.interfaces import IFactory
from zope.app.pagetemplate.simpleviewclass import simple as SimpleView
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.app import zapi
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.site.folder import SiteManagementFolder 
from zope.app.servicenames import Services

class IToolType(IInterface):
    """Interfaces implementing the tool type are considered tools."""

class IToolsView(IBrowserView):

    folder = Attribute("Name of the folder the tools are stored in.")

    title = Attribute("Title for the view.")

    description = Attribute("Description for the view.")

    def addTool(self):
        """Add a tool to the Site Manager.

        This method is responsible of creating the correct folder, if
        necessary, and forward the user to the adding screen.
        """

    def update(self):
        """Update the data."""

    def getComponents(self):
        """Return a list of components."""


class IUtilityToolsView(IToolsView):

    interface = Attribute("Interface the utility provides.")


class ToolsOverview:
    def getTools(self):
        tools = []
        for n, iface in zapi.getUtilitiesFor(None, IToolType):
            name = iface.getName()
            view = zapi.getView(self.context, 'manage%sTool.html' % name,
                                self.request)
            tools.append({'title':view.title,
                          'description':view.description,
                          'action':'./@@manage%sTool.html' % name })
        return tools

class ToolsBacklink:
    def getLink(self):
        service = zapi.getService(self.context, Services)
        iface = zapi.queryType(self.context, IToolType)
        url = '%s/manage%sTool.html' %(zapi.getPath(service), iface.getName())

        return self.request.response.redirect(url)

        
class UtilityToolsView(SimpleView):
    """Tools view for utilities."""

    implements(IUtilityToolsView)

    index = ViewPageTemplateFile('tool.pt')

    interface = None
    folder = None
    title = None
    description = None

    def addTool(self):
        if not self.folder in self.context:
            self.context[self.folder] = SiteManagementFolder()
        link = './%s/AddUtilityTool?interface=%s' %(self.folder, self.interface)
        return self.request.response.redirect(link)

    def update(self):
        return ''
    
    def getComponents(self):
        utils = zapi.getService(self.context, 'Utilities')
        items = []
        for iface, reg_name, stack in \
                utils.getRegisteredMatching(self.interface):
            info = stack.info()
            component = info[0]['registration'].getComponent()
            parent = zapi.getParent(component)
            items.append({
                'name': reg_name,
                'url': zapi.getPath(component),
                'parent_url': zapi.getPath(parent),
                'parent_name': zapi.name(parent),                
                'active': stack.active()})
        return items


class UtilityToolsViewFactory(object):
    """A factory that creates a tools view for a utility"""
    implements(IFactory)

    def __init__(self, interface, folder="tools", title=None, description=None):
        self._interface = interface
        self._folder = folder
        self._title = title
        self._description = description

        # See IFactory
        self.title = "Tools for '%s' Utility" %(interface.getName())
        self.description = self.title

    def __call__(self, context, request):
        tools = UtilityToolsView(context, request)
        tools.interface = self._interface
        tools.folder = self._folder
        tools.title = self._title
        tools.description = self._description
        return tools

    def getInterfaces(self):
        return implementedBy(self._class)


# class UtilityToolAdding(ComponentAdding):
#     """Adding subclass used for adding utilities."""
# 
#     menu_id = None
#     title = "Add Utility"
# 
#     _addFilterInterface = ILocalUtility
# 
#     def add(self, content):
#         # Override so as to check the type of the new object.
#         # XXX This wants to be generalized!
#         if not ILocalUtility.providedBy(content):
#             raise TypeError("%s is not a local utility" % content)
#         return super(UtilityAdding, self).add(content)
# 
#     def nextURL(self):
#         v = zapi.queryView(
#             self.added_object, "addRegistration.html", self.request)
#         if v is not None:
#             url = str(
#                 zapi.getView(self.added_object, 'absolute_url', self.request))
#             return url + "/addRegistration.html"
# 
#         return super(UtilityAdding, self).nextURL()
