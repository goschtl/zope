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
"""View support for adding and configuring services and other components.

$Id: service.py,v 1.26 2003/05/27 14:18:09 jim Exp $
"""

from zope.app.browser.container.adding import Adding
from zope.app.browser.container.contents import Contents
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.configuration import Registered, Active
from zope.app.interfaces.services.configuration import Unregistered
from zope.app.interfaces.services.service import ILocalService
from zope.app.interfaces.services.service import IServiceManager
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.pagetemplate import ViewPageTemplateFile
from zope.app.services.folder import SiteManagementFolder
from zope.app.services.service import ServiceConfiguration
from zope.app.traversing import traverse, getPath, getParent, objectName
from zope.component import getServiceManager
from zope.component import getView, getAdapter, queryView
from zope.context import ContextSuper
from zope.context import getWrapperContainer
from zope.publisher.browser import BrowserView

class ComponentAdding(Adding):
    """Adding subclass used for configurable components."""

    menu_id = "add_component"

    def add(self, content):
        # Override so as to save a reference to the added object
        self.added_object = ContextSuper(ComponentAdding, self).add(content)
        return self.added_object

    def nextURL(self):
        v = queryView(self.added_object, "addConfiguration.html", self.request)
        if v is not None:
            url = str(getView(self.added_object, 'absolute_url', self.request))
            return url + "/@@addConfiguration.html"

        return ContextSuper(ComponentAdding, self).nextURL()

    def action(self, type_name, id):
        if type_name == "../AddService":
            # Special case
            url = type_name
            if id:
                url += "?id=" + id
            self.request.response.redirect(url)
            return

        if not id:
            # Generate an id from the type name
            id = type_name
            l = id.rfind('.')
            if l >= 0:
                id = id[l+1:]
            i = 1
            while ("%s-%s" % (id, i)) in self.context:
                i=i+1
            id = "%s-%s" % (id, i)

        # Call the superclass action() method.
        # As a side effect, self.added_object is set by add() above.
        ContextSuper(ComponentAdding, self).action(type_name, id)

class ServiceAdding(ComponentAdding):
    """Adding subclass used for adding services."""

    menu_id = "add_service"

    def add(self, content):
        # Override so as to check the type of the new object.
        # XXX This wants to be generalized!
        if not ILocalService.isImplementedBy(content):
            raise TypeError("%s is not a local service" % content)

        return ContextSuper(ServiceAdding, self).add(content)

class UtilityAdding(ComponentAdding):
    """Adding subclass used for adding utilities."""

    menu_id = "add_utility"

    def add(self, content):
        # Override so as to check the type of the new object.
        # XXX This wants to be generalized!
        if not ILocalUtility.isImplementedBy(content):
            raise TypeError("%s is not a local utility" % content)
        return ContextSuper(UtilityAdding, self).add(content)

class ConnectionAdding(ComponentAdding):
    """Adding subclass used for adding database connections."""

    menu_id = "add_connection"

class CacheAdding(ComponentAdding):
    """Adding subclass used for adding caches."""

    menu_id = "add_cache"


class AddServiceConfiguration(BrowserView):
    """A view on a service implementation, used by add_svc_config.py."""

    def listServiceTypes(self):

        # Collect all defined services interfaces that it implements.
        sm = getServiceManager(self.context)
        lst = []
        for servicename, interface in sm.getServiceDefinitions():
            if interface.isImplementedBy(self.context):
                registry = sm.queryConfigurations(servicename)
                checked = True
                if registry and registry.active():
                    checked = False
                d = {'name': servicename, 'checked': checked}
                lst.append(d)
        return lst

    def action(self, name=[], active=[]):
        path = getPath(self.context)
        configure = getWrapperContainer(self.context).getConfigurationManager()
        container = getAdapter(configure, IZopeContainer)

        for nm in name:
            sc = ServiceConfiguration(nm, path, self.context)
            name = container.setObject("", sc)
            sc = container[name]
            if nm in active:
                sc.status = Active
            else:
                sc.status = Registered

        self.request.response.redirect("@@SelectedManagementView.html")


class ServiceSummary(BrowserView):
    """A view on the service manager, used by services.pt."""

    def update(self):
        """Possibly delete one or more services.

        In that case, issue a message.
        """
        todo = self.request.get("selected")
        doActivate = self.request.get("Activate")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not todo:
            if doDeactivate or doDelete:
                return "Please select at least one checkbox"
            return None
        if doActivate:
            return self._activate(todo)
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _activate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryConfigurations(name)
            obj = registry.active()
            if obj is None:
                # Activate the first registered configuration
                obj = registry.info()[0]['configuration']
                obj.status = Active
                done.append(name)
        if done:
            return "Activated: " + ", ".join(done)
        else:
            return "All of the checked services were alrady active"

    def _deactivate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryConfigurations(name)
            obj = registry.active()
            if obj is not None:
                obj.status = Registered
                done.append(name)
        if done:
            return "Deactivated: " + ", ".join(done)
        else:
            return "None of the checked services were active"

    def _delete(self, todo):
        errors = []
        for name in todo:
            registry = self.context.queryConfigurations(name)
            assert registry
            if registry.active() is not None:
                errors.append(name)
                continue
        if errors:
            return ("Can't delete active service%s: %s; "
                    "use the Deactivate button to deactivate" %
                    (len(errors) != 1 and "s" or "", ", ".join(errors)))

        # 1) Delete the registrations
        services = {}
        for name in todo:
            registry = self.context.queryConfigurations(name)
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['configuration']
                obj = conf.getComponent()
                path = getPath(obj)
                services[path] = obj
                conf.status = Unregistered
                parent = getParent(conf)
                name = objectName(conf)
                container = getAdapter(parent, IZopeContainer)
                del container[name]

        # 2) Delete the service objects
        # XXX Jim doesn't like this very much; he thinks it's too much
        #     magic behind the user's back.  OTOH, Guido believes that
        #     we're providing an abstraction here that hides the
        #     existence of the folder and its registration manager as
        #     much as possible, so it's appropriate to clean up when
        #     deleting a service; if you don't want that, you can
        #     manipulate the folder explicitly.
        for path, obj in services.items():
            parent = getParent(obj)
            name = objectName(obj)
            container = getAdapter(parent, IZopeContainer)
            del container[name]

        return "Deleted: %s" % ", ".join(todo)

    def listConfiguredServices(self):
        names = list(self.context.listConfigurationNames())
        names.sort()

        items = []
        for name in names:
            registry = self.context.queryConfigurations(name)
            assert registry
            infos = [info for info in registry.info() if info['active']]
            if infos:
                configobj = infos[0]['configuration']
                component = configobj.getComponent()
                url = str(getView(component, 'absolute_url', self.request))
            else:
                url = ""
            items.append({'name': name, 'url': url})

        return items


class ServiceActivation(BrowserView):
    """A view on the service manager, used by serviceactivation.pt.

    This really wants to be a view on a configuration registry
    containing service configurations, but registries don't have names,
    so we make it a view on the service manager; the request parameter
    'type' determines which service is to be configured."""

    def isDisabled(self):
        sm = getServiceManager(self.context)
        registry = sm.queryConfigurations(self.request.get('type'))
        return not (registry and registry.active())

    def listRegistry(self):
        sm = getServiceManager(self.context)
        registry = sm.queryConfigurations(self.request.get('type'))
        if not registry:
            return []

        # XXX this code path is not being tested
        result = []
        for info in registry.info():
            configobj = info['configuration']
            component = configobj.getComponent()
            path = getPath(component)
            path = path.split("/")
            info['name'] = "/".join(path[-2:])
            info['url'] = str(getView(component, 'absolute_url', self.request))
            info['config'] = str(getView(configobj, 'absolute_url',
                                         self.request))
            result.append(info)
        return result

    def update(self):
        active = self.request.get("active")
        if not active:
            return ""

        sm = getServiceManager(self.context)
        registry = sm.queryConfigurations(self.request.get('type'))
        if not registry:
            return "Invalid service type specified"
        old_active = registry.active()
        if active == "None":
            new_active = None
        else:
            new_active = traverse(sm, active)
        if old_active == new_active:
            return "No change"

        if new_active is None:
            old_active.status = Registered
            return "Service deactivated"
        else:
            new_active.status = Active
            return active + " activated"


class SiteManagementFoldersContents(Contents):

    __used_for__ = IServiceManager

    index = ViewPageTemplateFile('sitemanagement_contents.pt')

    def addSiteManagementFolder(self, name):
        self.context.setObject(name, SiteManagementFolder())
        self.request.response.redirect('@@contents.html')

