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
"""Use-Configuration view for utilities.

$Id: useconfiguration.py,v 1.6 2003/04/30 15:15:30 gvanrossum Exp $
"""

from zope.app.browser.component.interfacewidget import InterfaceWidget
from zope.app.browser.services.configuration import AddComponentConfiguration
from zope.app.form.widget import CustomWidget
from zope.app.interfaces.container import IZopeContainer
from zope.app.interfaces.services.configuration import Unregistered, Registered
from zope.app.traversing import getPath, getParent, objectName
from zope.component import getServiceManager, getView, getAdapter
from zope.interface.implements import flattenInterfaces
from zope.proxy.introspection import removeAllProxies
from zope.publisher.browser import BrowserView


class UtilityInterfaceWidget(InterfaceWidget):
    """Custom widget to select an interface from the component's interfaces.
    """

    def __call__(self):
        field = self.context
        component = field.context
        # XXX Have to remove proxies because flattenInterfaces
        #     doesn't work with proxies.
        bare = removeAllProxies(component)
        # Compute the list of interfaces that the component implements
        interfaces = [
            interface
            for interface in flattenInterfaces(bare.__implements__)
            if list(interface) # Does the interface define any names
            ]
        result = ['\n<select name="%s">' % self.name]
        for interface in interfaces:
            result.append('  <option value="%s.%s">%s</option>' %
                          (interface.__module__, interface.__name__,
                           interface.__name__))
        result.append('</select>')
        return '\n'.join(result)
        

class AddConfiguration(AddComponentConfiguration):
    """View for adding a utility configuration.


    We could just use AddComponentConfiguration, except that we need a
    custom interface widget.

    This is a view on a local utility, configured by an <addform>
    directive.
    """

    interface = CustomWidget(UtilityInterfaceWidget)


class Utilities(BrowserView):

    # self.context is the local utility service

    def update(self):
        """Possibly delete one or more utilities.

        In that case, issue a message.
        """
        selected = self.request.get("selected")
        doDeactivate = self.request.get("Deactivate")
        doDelete = self.request.get("Delete")
        if not selected:
            if doDeactivate or doDelete:
                return "Please select at least one checkbox"
            return None
        sm = getServiceManager(self.context)
        todo = []
        for key in selected:
            name, ifacename = key.split(":", 1)
            iface = sm.resolve(ifacename)
            todo.append((key, name, iface))
        if doDeactivate:
            return self._deactivate(todo)
        if doDelete:
            return self._delete(todo)

    def _deactivate(self, todo):
        done = []
        for key, name, iface in todo:
            registry = self.context.queryConfigurations(name, iface)
            obj = registry.active()
            if obj is not None:
                obj.status = Registered
                done.append(key)
        if done:
            return "Deactivated: " + ", ".join(done)
        else:
            return "None of the checked utilities were active"

    def _delete(self, todo):
        errors = []
        for key, name, iface in todo:
            registry = self.context.queryConfigurations(name, iface)
            assert registry
            if registry.active() is not None:
                errors.append(key)
                continue
        if errors:
            return ("Can't delete active utilit%s: %s; "
                    "use the Deactivate button to deactivate" %
                    (len(errors) != 1 and "ies" or "y", ", ".join(errors)))

        # 1) Delete the registrations
        services = {}
        for key, name, iface in todo:
            registry = self.context.queryConfigurations(name, iface)
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
        for path, obj in services.items():
            parent = getParent(obj)
            name = objectName(obj)
            container = getAdapter(parent, IZopeContainer)
            del container[name]

        return "Deleted: %s" % ", ".join([key for key, name, iface in todo])

    def getConfigs(self):
        L = []
        for iface, name, cr in self.context.getRegisteredMatching():
            active = cr.active()
            ifname = _interface_name(iface)
            d = {"interface": ifname,
                 "name": name,
                 "url": "",
                 "configurl": ("@@configureutility.html?interface=%s&name=%s"
                               % (ifname, name)),
                 }
            if active is not None:
                d["url"] = str(getView(active.getComponent(),
                                       "absolute_url",
                                       self.request))
            L.append((ifname, name, d))
        L.sort()
        return [d for ifname, name, d in L]


class ConfigureUtility(BrowserView):
    def update(self):
        sm = getServiceManager(self.context)
        iface = sm.resolve(self.request['interface'])
        name = self.request['name']
        cr = self.context.queryConfigurations(name, iface)
        form = getView(cr, "ChangeConfigurations", self.request)
        form.update()
        return form


def _interface_name(iface):
    return "%s.%s" % (iface.__module__, iface.__name__)
