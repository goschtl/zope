##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Use-Registration view for utilities.

$Id: __init__.py,v 1.7 2003/07/02 17:52:41 fdrake Exp $
"""

from zope.app.browser.component.interfacewidget import InterfaceWidget
from zope.app.browser.services.registration import AddComponentRegistration
from zope.app.form.widget import CustomWidget
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.registration import ActiveStatus
from zope.app.interfaces.services.registration import RegisteredStatus
from zope.app.interfaces.services.registration import UnregisteredStatus
from zope.app import zapi
from zope.interface import providedBy
from zope.proxy import removeAllProxies
from zope.publisher.browser import BrowserView


class UtilityInterfaceWidget(InterfaceWidget):
    """Custom widget to select an interface from the component's interfaces.
    """

    def __call__(self):
        field = self.context
        component = field.context
        result = ['\n<select name="%s">' % self.name]
        for interface in providedBy(component).flattened():
            result.append('  <option value="%s.%s">%s</option>' %
                          (interface.__module__, interface.__name__,
                           interface.__name__))
        result.append('</select>')
        return '\n'.join(result)
        

class AddRegistration(AddComponentRegistration):
    """View for adding a utility registration.


    We could just use AddComponentRegistration, except that we need a
    custom interface widget.

    This is a view on a local utility, configured by an <addform>
    directive.
    """

    interface_widget = CustomWidget(UtilityInterfaceWidget)


class Utilities(BrowserView):

    # self.context is the local utility service

    def update(self):
        """Possibly delete one or more utilities.

        In that case, issue a message.
        """
        selected = self.request.get("selected")
        doActivate = self.request.get("Activate")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not selected:
            if doActivate or doDeactivate or doDelete:
                return "Please select at least one checkbox"
            return None
        folder = zapi.getParent(self.context)
        todo = []
        for key in selected:
            name, ifacename = key.split(":", 1)
            iface = folder.resolve(ifacename)
            todo.append((key, name, iface))
        if doActivate:
            return self._activate(todo)
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _activate(self, todo):
        done = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            obj = registry.active()
            if obj is None:
                # Activate the first registered registration
                obj = registry.info()[0]['registration']
                obj.status = ActiveStatus
                done.append(obj.usageSummary())
        if done:
            return "Activated: " + ", ".join(done)
        else:
            return "All of the checked utilities were already active"

    def _deactivate(self, todo):
        done = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            obj = registry.active()
            if obj is not None:
                obj.status = RegisteredStatus
                done.append(obj.usageSummary())
        if done:
            return "Deactivated: " + ", ".join(done)
        else:
            return "None of the checked utilities were active"

    def _delete(self, todo):
        errors = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            assert registry
            obj = registry.active()
            if obj is not None:
                errors.append(obj.usageSummary())
                continue
        if errors:
            return ("Can't delete active utilit%s: %s; "
                    "use the Deactivate button to deactivate" %
                    (len(errors) != 1 and "ies" or "y", ", ".join(errors)))

        # 1) Delete the registrations
        services = {}
        done = []
        for key, name, iface in todo:
            registry = self.context.queryRegistrations(name, iface)
            assert registry
            assert registry.active() is None # Phase error
            first = True
            for info in registry.info():
                conf = info['registration']
                obj = conf.getComponent()
                if first:
                    done.append(conf.usageSummary())
                    first = False
                path = zapi.getPath(obj)
                services[path] = obj
                conf.status = UnregisteredStatus
                parent = zapi.getParent(conf)
                name = zapi.getName(conf)
                container = zapi.getAdapter(parent, IZopeContainer)
                del container[name]

        # 2) Delete the service objects
        for path, obj in services.items():
            parent = zapi.getParent(obj)
            name = zapi.getName(obj)
            container = zapi.getAdapter(parent, IZopeContainer)
            del container[name]

        return "Deleted: %s" % ", ".join(done)

    def getConfigs(self):
        L = []
        for iface, name, cr in self.context.getRegisteredMatching():
            active = obj = cr.active()
            if obj is None:
                obj = cr.info()[0]['registration'] # Pick a representative
            ifname = _interface_name(iface)
            d = {"interface": ifname,
                 "name": name,
                 "url": "",
                 "summary": obj.usageSummary(),
                 "configurl": ("@@configureutility.html?interface=%s&name=%s"
                               % (ifname, name)),
                 }
            if active is not None:
                d["url"] = str(zapi.getView(active.getComponent(),
                                            "absolute_url",
                                            self.request))
            L.append((ifname, name, d))
        L.sort()
        return [d for ifname, name, d in L]


class ConfigureUtility(BrowserView):
    def update(self):
        folder = zapi.getParent(self.context)
        iface = folder.resolve(self.request['interface'])
        name = self.request['name']
        iface = removeAllProxies(iface)
        regstack = self.context.queryRegistrations(name, iface)
        form = zapi.getView(regstack, "ChangeRegistrations", self.request)
        form.update()
        return form


def _interface_name(iface):
    return "%s.%s" % (iface.__module__, iface.__name__)
