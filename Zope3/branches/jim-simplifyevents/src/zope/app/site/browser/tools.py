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

$Id$
"""
from zope.interface import implements, Attribute
from zope.interface.interfaces import IInterface
from zope.component.interfaces import IFactory
from zope.app.pagetemplate.simpleviewclass import simple as SimpleView
from zope.app.publisher.interfaces.browser import IBrowserView
from zope.app import zapi
from zope.app.copypastemove import rename
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from zope.app.site.folder import SiteManagementFolder 
from zope.app.servicenames import Services, Utilities
from zope.app.utility.browser import AddRegistration
from zope.app.utility import UtilityRegistration
from zope.app.site.browser import ComponentAdding
from zope.app.site.folder import SiteManagementFolder
from zope.app.registration.interfaces import UnregisteredStatus
from zope.app.registration.interfaces import RegisteredStatus
from zope.app.registration.interfaces import ActiveStatus
from zope.app.site.interfaces import ILocalService
from zope.app.site.browser import ServiceAdding

from zope.app.i18n import ZopeMessageIDFactory as _


class IToolType(IInterface):
    """Interfaces implementing the tool type are considered tools."""

class IToolView(IBrowserView):

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


class IUtilityToolView(IToolView):

    interface = Attribute("Interface the utility provides.")


class ToolsOverview:
    def getTools(self):
        tools = []
        for n, iface in zapi.getUtilitiesFor(IToolType):
            name = iface.getName()
            view = zapi.getView(self.context, 'manage%sTool.html' % name,
                                self.request)
            tools.append({'title':view.title,
                          'description':view.description,
                          'action':'./@@manage%sTool.html' % name })
        return tools

class ToolsBacklink:
    def getLink(self):
        service = zapi.getService(Services)
        iface = zapi.queryType(self.context, IToolType)
        url = '%s/manage%sTool.html' %(zapi.getPath(service), iface.getName())

        return self.request.response.redirect(url)


class ServiceToolView(SimpleView):
    """Tools view for services."""
    implements(IToolView)

    index = ViewPageTemplateFile('tool.pt')

    folder = None
    title = None
    description = None

    can_rename = False

    def addTool(self):
        if not self.folder in self.context:
            self.context[self.folder] = SiteManagementFolder()
        link = './%s/AddServiceTool' %self.folder
        return self.request.response.redirect(link)

    def delete(self):
        for name in self.request.form['selected']:
            reg = self.context.queryRegistrations(name)

            del_objs = []

            # Delete registrations
            for info in reg.info():
                conf = info['registration']
                obj = conf.getComponent()
                conf.status = UnregisteredStatus
                reg_folder = zapi.getParent(conf)
                name = zapi.name(conf)
                del reg_folder[name]
                if obj not in [c.getComponent()
                               for c in reg_folder.values()]:
                    del_objs.append(obj)

            # Delete object, if no other registration is available.
            for obj in del_objs:
                parent = zapi.getParent(obj)
                name = zapi.name(obj)
                del parent[name]


    def activate(self):
        for name in self.request.form['selected']:
            reg = self.context.queryRegistrations(name)
            # Activate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = ActiveStatus
        
    def deactivate(self):
        for name in self.request.form['selected']:
            reg = self.context.queryRegistrations(name)
            # Deactivate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = RegisteredStatus

    def update(self):
        status = ''
        self.renameList = []
        
        if self.request.form.has_key('ADD'):
            self.request.response.redirect('./AddServiceTool')
        elif self.request.form.has_key('DELETE'):
            self.delete()
            status = _('Deleted selected tools.')
        elif self.request.form.has_key('APPLY_RENAME'):
            self.rename()
            status = _('Renamed selected tools.')         
        elif self.request.form.has_key('REFRESH'):
            pass
        elif self.request.form.has_key('ACTIVATE'):
            self.activate()
            status = _('Activated registrations.')
        elif self.request.form.has_key('DEACTIVATE'):
            self.deactivate()
            status = _('Deactivated registrations.')
            
        return status
    
    def getComponents(self):
        items = []
        
        for name in self.context.listRegistrationNames():
            registry = self.context.queryRegistrations(name)

            configobj = registry.info()[0]['registration']
            component = configobj.getComponent()
            url = str(
                zapi.getView(component, 'absolute_url', self.request))
            parent = zapi.getParent(component)
            items.append( {'name': name,
                           'url': url,
                           'parent_url': zapi.getPath(parent),
                           'parent_name':zapi.name(parent),
                           'active':registry.info()[0]['active'] })
        
        return items

class ServiceToolAdding(ServiceAdding):
    """Adding subclass used for adding utilities."""

    title = "Add Service Tool"
    folder = "tools"

    def addingInfo(self):
        if self.folder not in self.context:
            self.context[self.folder] = SiteManagementFolder()
        self.context = self.context[self.folder]
        return super(ServiceToolAdding, self).addingInfo()

    def add(self, content):
        self.context = self.context[self.folder]
        return super(ServiceToolAdding, self).add(content)
    
    def nextURL(self):
        return '../@@manageILocalServiceTool.html'


class UtilityToolView(SimpleView):
    """Tools view for utilities."""

    implements(IUtilityToolView)

    index = ViewPageTemplateFile('tool.pt')

    interface = None
    folder = None
    title = None
    description = None

    can_rename = True

    def addTool(self):
        if not self.folder in self.context:
            self.context[self.folder] = SiteManagementFolder()
        link = './%s/AddUtilityTool?interface=%s' %(self.folder, self.interface)
        return self.request.response.redirect(link)

    def delete(self):
        for name in self.request.form['selected']:
            utils = zapi.getService(self, Utilities)
            reg = utils.queryRegistrations(name, self.interface)

            del_objs = []

            # Delete registrations
            for info in reg.info():
                conf = info['registration']
                obj = conf.getComponent()
                conf.status = UnregisteredStatus
                reg_folder = zapi.getParent(conf)
                name = zapi.name(conf)
                del reg_folder[name]
                if obj not in [c.getComponent()
                               for c in reg_folder.values()]:
                    del_objs.append(obj)

            # Delete object, if no other registration is available.
            for obj in del_objs:
                parent = zapi.getParent(obj)
                name = zapi.name(obj)
                del parent[name]

    def rename(self):
        for name in self.request.form['old_names']:
            newname = self.request.form['new_names'][
                self.request.form['old_names'].index(name)]
            
            utils = zapi.getService(self, 'Utilities')
            reg = utils.queryRegistrations(name, self.interface)

            # Rename registrations
            for info in reg.info():
                conf = info['registration']
                orig_status = conf.status
                conf.status = UnregisteredStatus
                conf.name = newname
                conf.status = orig_status

    def activate(self):
        for name in self.request.form['selected']:
            utils = zapi.getService(self, 'Utilities')
            reg = utils.queryRegistrations(name, self.interface)

            # Activate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = ActiveStatus
        
    def deactivate(self):
        for name in self.request.form['selected']:
            utils = zapi.getService(self, 'Utilities')
            reg = utils.queryRegistrations(name, self.interface)

            # Deactivate registrations
            for info in reg.info():
                conf = info['registration']
                conf.status = RegisteredStatus

    def update(self):
        status = ''
        self.renameList = []
        
        if self.request.form.has_key('ADD'):
            self.request.response.redirect('./Add%sTool' %
                                           self.interface.getName())
        elif self.request.form.has_key('DELETE'):
            self.delete()
            status = _('Deleted selected tools.')
        elif self.request.form.has_key('RENAME'):
            self.renameList = self.request.form.get('selected', [])
        elif self.request.form.has_key('APPLY_RENAME'):
            self.rename()
            status = _('Renamed selected tools.')         
        elif self.request.form.has_key('REFRESH'):
            pass
        elif self.request.form.has_key('ACTIVATE'):
            self.activate()
            status = _('Activated registrations.')
        elif self.request.form.has_key('DEACTIVATE'):
            self.deactivate()
            status = _('Deactivated registrations.')
            
        return status
    
    def getComponents(self):
        utils = zapi.getService(self.context, Utilities)
        items = []
        for registration in [reg for reg in utils.registrations(localOnly=True)
                             if reg.provided == self.interface]:

            stack = utils.queryRegistrationsFor(registration)
            parent = zapi.getParent(registration.component)
            items.append({
                'name': registration.name,
                'url': zapi.getPath(registration.component),
                'parent_url': zapi.getPath(parent),
                'parent_name': zapi.name(parent),                
                'active': stack.active()})

        return items


class UtilityToolAdding(ComponentAdding):
    """Adding subclass used for adding utilities."""

    menu_id = None
    title = "Add Tool"
    folder = "tools"
    _addFilterInterface = None


    def addingInfo(self):
        if self.folder not in self.context:
            self.context[self.folder] = SiteManagementFolder()
        self.context = self.context[self.folder]
        return super(UtilityToolAdding, self).addingInfo()

    def add(self, content):
        if not self._addFilterInterface.providedBy(content):
            raise TypeError("%s is not a %s" %(
                content, self._addFilterInterface.getName()))
        self.context = self.context[self.folder]
        util = super(UtilityToolAdding, self).add(content)
        
        # Add registration
        registration = UtilityRegistration(self.contentName,
                                           self._addFilterInterface,
                                           zapi.getPath(util))
        reg_view = AddRegistration(content, self.request)
        reg_view.add(registration)
        
        return util

    def nextURL(self):
        return '../@@manage%sTool.html' %self._addFilterInterface.getName()
