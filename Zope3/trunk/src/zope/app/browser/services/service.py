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

$Id: service.py,v 1.15 2003/03/21 21:00:28 jim Exp $
"""

from zope.app.browser.container.adding import Adding
from zope.component import getView, getAdapter, queryView
from zope.proxy.context import ContextWrapper, ContextSuper
from zope.app.interfaces.container import IZopeContainer
from zope.component import getServiceManager
from zope.publisher.browser import BrowserView
from zope.app.services.service import ServiceConfiguration
from zope.app.interfaces.services.configuration import IConfiguration
from zope.app.form.utility import setUpWidgets, getWidgetsDataForContent
from zope.app.traversing import traverse, getPath
from zope.app.interfaces.services.service import ILocalService
from zope.proxy.context import getWrapperContainer
from zope.app.interfaces.services.configuration \
     import Unregistered, Registered, Active

__metaclass__ = type

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
            url = getPath(self.added_object)
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
        configure = traverse(getWrapperContainer(self.context), 'configure')
        container = getAdapter(configure, IZopeContainer)

        for nm in name:
            # XXX Shouldn't hardcode 'configure'
            sc = ServiceConfiguration(nm, path, self.context)
            name = container.setObject("", sc)
            sc = container[name]
            if nm in active:
                sc.status = Active
            else:
                sc.status = Registered

        self.request.response.redirect("@@useConfiguration.html")


class ServiceSummary(BrowserView):
    """A view on the service manager, used by services.pt."""

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
