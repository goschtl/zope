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

$Id: __init__.py,v 1.6 2003/10/29 20:33:08 sidnei Exp $
"""

from zope.app import zapi
from zope.app.browser.container.adding import Adding
from zope.app.i18n import ZopeMessageIDFactory as _
from zope.app.interfaces.container import INameChooser
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.service import ILocalService
from zope.app.interfaces.services.utility import ILocalUtility
from zope.app.services.service import ServiceRegistration
from zope.publisher.browser import BrowserView
from zope.app.interfaces.services.service import ISite
from zope.app.services.service import ServiceManager

class ComponentAdding(Adding):
    """Adding subclass used for registerable components."""

    menu_id = "add_component"

    def add(self, content):
        # Override so as to save a reference to the added object
        self.added_object = super(ComponentAdding, self).add(content)
        return self.added_object

    def nextURL(self):
        v = zapi.queryView(
            self.added_object, "registration.html", self.request)
        if v is not None:
            url = str(
                zapi.getView(self.added_object, 'absolute_url', self.request))
            return url + "/@@registration.html"

        return super(ComponentAdding, self).nextURL()

    def action(self, type_name, id):
        # For special case of that we want to redirect to another adding view
        # (usually another menu such as AddService)
        if type_name.startswith("../"):
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
        super(ComponentAdding, self).action(type_name, id)

class ServiceAdding(ComponentAdding):
    """Adding subclass used for adding services."""

    menu_id = "add_service"

    def add(self, content):
        # Override so as to check the type of the new object.
        # XXX This wants to be generalized!
        if not ILocalService.isImplementedBy(content):
            raise TypeError("%s is not a local service" % content)

        return super(ServiceAdding, self).add(content)


class UtilityAdding(ComponentAdding):
    """Adding subclass used for adding utilities."""

    menu_id = "add_utility"

    def add(self, content):
        # Override so as to check the type of the new object.
        # XXX This wants to be generalized!
        if not ILocalUtility.isImplementedBy(content):
            raise TypeError("%s is not a local utility" % content)
        return super(UtilityAdding, self).add(content)


class AddServiceRegistration(BrowserView):
    """A view on a service implementation, used by add_svc_config.py."""

    def listServiceTypes(self):

        # Collect all defined services interfaces that it implements.
        sm = zapi.getServiceManager(self.context)
        lst = []
        for servicename, interface in sm.getServiceDefinitions():
            if interface.isImplementedBy(self.context):
                registry = sm.queryRegistrations(servicename)
                checked = True
                if registry and registry.active():
                    checked = False
                d = {'name': servicename, 'checked': checked}
                lst.append(d)
        return lst

    def action(self, name=[], active=[]):
        path = zapi.name(self.context)
        rm = self.context.__parent__.getRegistrationManager()
        chooser = zapi.getAdapter(rm, INameChooser)

        for nm in name:
            sc = ServiceRegistration(nm, path, self.context)
            name = chooser.chooseName(nm, sc)
            rm[name] = sc
            if nm in active:
                sc.status = ActiveStatus
            else:
                sc.status = RegisteredStatus

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
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is None:
                # Activate the first registered registration
                obj = registry.info()[0]['registration']
                obj.status = ActiveStatus
                done.append(name)
        if done:
            s = _("Activated: ${activated_services}")
            s.mapping = {'activated_services': ", ".join(done)}
            return s
        else:
            return _("All of the checked services were already active")

    def _deactivate(self, todo):
        done = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(name)
        if done:
            s = _("Deactivated: ${deactivated_services}")
            s.mapping = {'deactivated_services': ", ".join(done)}
            return s
        else:
            return _("None of the checked services were active")

    def _delete(self, todo):
        errors = []
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            if registry.active() is not None:
                errors.append(name)
                continue
        if errors:
            s = _("Can't delete active service(s): ${service_names}; "
                  "use the Deactivate button to deactivate")
            s.mapping = {'service_names': ", ".join(errors)}
            return s

        # 1) Delete the registrations
        services = {}
        for name in todo:
            registry = self.context.queryRegistrations(name)
            assert registry
            assert registry.active() is None # Phase error
            for info in registry.info():
                conf = info['registration']
                obj = conf.getComponent()
                path = zapi.getPath(obj)
                services[path] = obj
                conf.status = UnregisteredStatus
                parent = zapi.getParent(conf)
                name = zapi.name(conf)
                del parent[name]

        # 2) Delete the service objects
        # XXX Jim doesn't like this very much; he thinks it's too much
        #     magic behind the user's back.  OTOH, Guido believes that
        #     we're providing an abstraction here that hides the
        #     existence of the folder and its registration manager as
        #     much as possible, so it's appropriate to clean up when
        #     deleting a service; if you don't want that, you can
        #     manipulate the folder explicitly.
        for path, obj in services.items():
            parent = zapi.getParent(obj)
            name = zapi.name(obj)
            del parent[name]

        s = _("Deleted: ${service_names}")
        s.mapping = {'service_names': ", ".join(todo)}
        return s

    def listConfiguredServices(self):
        names = list(self.context.listRegistrationNames())
        names.sort()

        items = []
        for name in names:
            registry = self.context.queryRegistrations(name)
            assert registry
            infos = [info for info in registry.info() if info['active']]
            if infos:
                configobj = infos[0]['registration']
                component = configobj.getComponent()
                url = str(
                    zapi.getView(component, 'absolute_url', self.request))
            else:
                url = ""
            items.append({'name': name, 'url': url})

        return items


class ServiceActivation(BrowserView):
    """A view on the service manager, used by serviceactivation.pt.

    This really wants to be a view on a registration registry
    containing service registrations, but registries don't have names,
    so we make it a view on the service manager; the request parameter
    'type' determines which service is to be configured."""

    def isDisabled(self):
        sm = zapi.getServiceManager(self.context)
        registry = sm.queryRegistrations(self.request.get('type'))
        return not (registry and registry.active())

    def listRegistry(self):
        sm = zapi.getServiceManager(self.context)
        registry = sm.queryRegistrations(self.request.get('type'))
        if not registry:
            return []

        # XXX this code path is not being tested
        result = []
        dummy = {'id': 'None',
                 'active': False,
                 'registration': None,
                 'name': '',
                 'url': '',
                 'config': '',
                }
        for info in registry.info(True):
            configobj = info['registration']
            if configobj is None:
                info = dummy
                dummy = None
                if not result:
                    info['active'] = True
            else:
                component = configobj.getComponent()
                path = zapi.getPath(component)
                path = path.split("/")
                info['name'] = "/".join(path[-2:])
                info['url'] = str(
                    zapi.getView(component, 'absolute_url', self.request))
                info['config'] = str(zapi.getView(configobj, 'absolute_url',
                                             self.request))
            result.append(info)
        if dummy:
            result.append(dummy)
        return result

    def update(self):
        active = self.request.get("active")
        if not active:
            return ""

        sm = zapi.getServiceManager(self.context)
        registry = sm.queryRegistrations(self.request.get('type'))
        if not registry:
            return _("Invalid service type specified")
        old_active = registry.active()
        if active == "None":
            new_active = None
        else:
            new_active = zapi.traverse(sm, active)
        if old_active == new_active:
            return _("No change")

        if new_active is None:
            registry.activate(None)
            return _("Service deactivated")
        else:
            new_active.status = ActiveStatus
            s = "${active_services} activated"
            s.mapping = {'active_services': active}
            return s

class MakeSite(BrowserView):
    """View for convering a possible site to a site
    """

    def addSiteManager(self):
        """Convert a possible site to a site

        XXX we should also initialize some user-selected services.

        >>> class PossibleSite:
        ...     def setSiteManager(self, sm):
        ...         from zope.interface import directlyProvides
        ...         directlyProvides(self, ISite)


        >>> folder = PossibleSite()

        >>> from zope.publisher.browser import TestRequest
        >>> request = TestRequest()

        Now we'll make out folder a site:

        >>> MakeSite(folder, request).addSiteManager()

        Now verify that we have a site:

        >>> ISite.isImplementedBy(folder)
        1

        Note that we've also redirected the request:

        >>> request.response.getStatus()
        302

        >>> request.response.getHeader('location')
        '++etc++site/'

        If we try to do it again, we'll fail:

        >>> MakeSite(folder, request).addSiteManager()
        Traceback (most recent call last):
        ...
        UserError: This is already a site


        """
        if ISite.isImplementedBy(self.context):
            raise zapi.UserError('This is already a site')
        sm = ServiceManager(self.context)
        self.context.setSiteManager(sm)
        self.request.response.redirect("++etc++site/")
